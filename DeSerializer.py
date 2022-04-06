from struct import pack 
from struct import unpack
from time import time
from Requirements import Requirements
from Signalhandler import init_timeout_err
from Signalhandler import remove_timeout_err

FORMAT = "utf-8"
FAIL = 255
SUCCESS = 0

EMPTY_VALUE = 0

ZERO_WORDS = 0

USER_RESPONSE_LIMIT = 15

CONNECTIVITY_CHECK = 0
ADD_WORDS = 1
GET_WORDS = 2
REMOVE_WORDS_BY_VALUE = 3
REMOVE_WORDS_BY_PREFIX = 4
ADD_WORDS_FROM_FILE = 5
QUIT = 6

MAX_BYTE = 65535
MAX_WORD_LENGTH = 19

def print_select_menu():
    print ('select a word from the list above' )

def print_success_search_menu(num_results):
    print('operation successful')
    print('number of results: ', num_results)

def get_trans_id():
    return int(time())%MAX_BYTE

def check_string(string_to_check):
    print(len(string_to_check))
    if (MAX_WORD_LENGTH < len(string_to_check)):
        print("********WORD EXCEEDS 20 CHARACTERS******************")
        return False
    else:
        return True 

def check_file_format(filename_to_check):
    print("Checking file")
    return filename_to_check.endswith('.txt')

def check_opcode(data_to_check):
    opcode = data_to_check[0]
    if opcode != FAIL:
        return True
    else:
        return False


class DeSerializer:

    def __init__(self):
        self.packet = b""
        self.trans_id = 0
        self.connectivity_packet = b""
    
    def make_trans_id(self):
        self.trans_id = get_trans_id()

    def make_header(self, opcode):
        self.opcode = opcode
        self.make_trans_id()
    
    def serialize_connectivity(self):
        self.make_trans_id()
        self.connectivity_packet = pack('!B H L B', EMPTY_VALUE,EMPTY_VALUE,self.trans_id,EMPTY_VALUE)

    def serialize_words_add(self):
        '''Serializes words provided by user and creates packet to send'''
        self.make_trans_id()
        words = input('> ')
        result = [x.strip() for x in words.split(',')]
        intlist = [len(x) for x in result]
        self.word_check(result, intlist)
        if (ZERO_WORDS == len(result)):
            print("None of the words met standard")
            self.packet = b""
            return
        bytes_words = [bytes(x, 'utf-8') for x in result]
        header = (self.opcode, len(result), self.trans_id,EMPTY_VALUE)
        net_bytes = pack('!B H L B',*header)
        bytes_ser = bytes()
        bytes_ser = bytes_ser.join((pack('!H {}s'.format(len(result[x])), intlist[x], bytes_words[x]) for x in range(len(result))))
        self.packet = b"".join([net_bytes, bytes_ser])
    
    def serialize_words_get(self):
        '''Serializes specifications provided by users to get words'''
        prefix = input('prefix: ')
        print(prefix)
        result = check_string(prefix)
        if not result:
            self.packet = b""
            return
        prefix = bytes(prefix, 'utf-8')
        user_requirements = Requirements()
        user_requirements.collect_requirements()
        header = (self.opcode,) + user_requirements.all_requirements
        net_bytes = pack('!B H H H B',*header)
        bytes_ser = pack('!H {}s'.format(len(prefix)),len(prefix), prefix)
        self.packet = b"".join([net_bytes,bytes_ser])
    
    def serialize_delete_words(self):
        '''Serializes specifications provided by users to delete words'''
        word_list = input('>  ')
        result = [x.strip() for x in word_list.split(',')]
        intlist = [len(x) for x in result]
        self.word_check(result, intlist)
        if (ZERO_WORDS == len(result)):
            print("None of the words met standard")
            self.packet = b""
            return
        bytes_words = [bytes(x, 'utf-8') for x in result]
        header = (self.opcode, len(result), self.trans_id,EMPTY_VALUE)
        net_bytes = pack('!B H L B',*header)
        bytes_ser = bytes()
        bytes_ser = bytes_ser.join((pack('!H {}s'.format(len(result[x])), intlist[x], bytes_words[x]) for x in range(len(result))))
        self.packet = b"".join([net_bytes, bytes_ser])

    def serialize_delete_word_prefix(self):
        '''Serializes specifications provided by users to delete words based on prefix'''
        header = (self.opcode, EMPTY_VALUE, self.trans_id,EMPTY_VALUE)
        net_bytes = pack('!B H L B',*header)
        bytes_ser = bytes()
        self.serialize_words_get()
        bytes_ser = self.packet
        self.packet =  b"".join([net_bytes, bytes_ser])
    
    def add_words_file(self, callback):
        '''Serializes words in a file provided by user. The packets will be split up into 1024 sized packets'''
        filename_user = input("Enter the file name (.txt format): ")
        result = check_file_format(filename_user)
        if not result:
            print("Is not a proper file to use")
            return
        size = 0
        num_words = 0
        num_packet = 0
        pre_size = 0
        packet = bytes()
        packet_list = []
        packet_sizes = []
        with open(filename_user, 'r') as file:
            for line in file:
                word = line.strip('\n')
                pre_size = (size + len(word) + 2)
                if ( pre_size > 1016):
                    print("---------------------------------------------------------- making new packet---------------------------")
                    packet = b"".join(packet_list)
                    print(packet)
                    header = (self.opcode, num_words, self.trans_id,None)
                    net_bytes = pack('!B H L B',*header)  
                    self.packet = b"".join([net_bytes, packet])
                    result = callback.send_req(self.packet, self.trans_id)
                    if(False == result):
                        self.packet = b""
                        return
                    server_response = callback.rec_req()
                    result = check_opcode(server_response)
                    if(False == result):
                        self.packet = b""
                        return
                    packet_list = []
                    num_packet = num_packet + 1
                    packet_sizes.append(size)
                    size = 0
                    packet = bytes()
                    num_words = 0
                    self.make_header(self.opcode)
                num_words = num_words + 1
                size += (len(word) + 2)
                packet_list.append(pack('!H {}s'.format(len(word)), len(word), bytes(word, 'utf-8')))
        
        packet = b"".join(packet_list)
        header = (self.opcode, num_words, self.trans_id,EMPTY_VALUE)
        net_bytes = pack('!B H L B',*header)  
        self.packet = b"".join([net_bytes, packet])    
        print(size)
        print(packet)
        print("The number of packets is : ", num_packet)
        print("The packet sizes are ", packet_sizes)

    def deserialize_words(self, word_list, string_list):
        '''Deserializes words from server'''
        num_words = int((unpack('!H', word_list[0:2]))[0])
        if(ZERO_WORDS == num_words):
            print('Server returned 0 words')
            return ZERO_WORDS
        else:
            print_success_search_menu(num_words)
            current_position = 7
            strn_len = 0
            for x in range(num_words):
                strn_len = int((unpack('!H ', word_list[current_position:current_position+2]))[0])
                print(strn_len)
                current_position += 2
                word_grabbed = (unpack('!{}s'.format(strn_len), word_list[current_position:current_position+strn_len]))[0].decode(FORMAT)
                print(word_grabbed)
                current_position += strn_len
                print(current_position)
                string_list.append(word_grabbed)
            return num_words
    def deserialize_data(self, response, client_callback):
        '''Deserializes packet sent from server'''
        print(response[0])
        print(response)
        opcode = response[0]
        transaction_to_note = response[3:7]
        print(transaction_to_note)
        if opcode != FAIL:
            if opcode == CONNECTIVITY_CHECK:
                print('-------------------------------------------------')
                print("Connectivity check complete [", unpack('!I', transaction_to_note)[0], "]")
                return True
            elif opcode == ADD_WORDS:
                print('-------------------------------------------------')
                print("Words added! [", unpack('!L', transaction_to_note)[0], "]")
            elif opcode== GET_WORDS:
                self.deserialize_words_respond(response[1:], client_callback)
            elif opcode== REMOVE_WORDS_BY_VALUE:
                print('-------------------------------------------------')
                print("Words removed by value! [", unpack('!L', transaction_to_note)[0], "]")
            elif opcode== REMOVE_WORDS_BY_PREFIX:
                print('-------------------------------------------------')
                print("Words removed by prefix! [", unpack('!L', transaction_to_note)[0], "]")
                string_list = []
                self.deserialize_words(response[1:], string_list)
                self.print_list_words(string_list)
            else:
                print("Invalid response from server. Recommend connectivity check")
        else:
            print('-------------------------------------------------')
            print("Failed on transaction ", unpack('!L', transaction_to_note)[0])
        return False
    
    def deserialize_words_respond(self, word_list, callback):
        '''Deserializes words sent from server. User must respond'''
        string_list = []
        num_words = self.deserialize_words(word_list, string_list)
        if ( ZERO_WORDS == num_words):
            self.packet = pack('!H H', EMPTY_VALUE, EMPTY_VALUE)
            callback.send_resp(self.packet)
            return
        else:
            init_timeout_err()
            print_select_menu()
            self.print_list_words(string_list)
            try:
                select = input('> ')
                if select:
                    if select in string_list:
                        strn_len = len(select)
                        select = bytes(select, 'utf-8')
                        self.packet = pack('!H {}s'.format(strn_len), strn_len, select)
                    else:
                        print('INVALID WORD.....exiting')
                        self.packet = pack('!H H', EMPTY_VALUE, EMPTY_VALUE)
                else:
                    self.packet = pack('!H H', EMPTY_VALUE, EMPTY_VALUE)
    
                callback.send_resp(self.packet)
            except TimeoutError:
                print("USER TOOK TOO LONG")
            finally:
                remove_timeout_err()

    def word_check(self, word_list, word_int_list):
        '''Integrity check of user's input'''
        index = 0
        for x in list(word_int_list):
            if x > MAX_WORD_LENGTH:
                bad_word = word_list[index]
                print(bad_word, "exceeds 19 characters!!!")
                word_list.remove(bad_word)
                word_int_list.remove(x)
            else:
                index = index + 1
        
        print(len(word_list))

    def print_list_words(self, string_list):
        '''Prints provided word list'''
        print('words:')
        for x in string_list:
            print(x)
            
                