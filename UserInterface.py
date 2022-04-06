from os import system
from DeSerializer import *


class UserInterface:
    def __init__(self):
        self.continue_asking = True
        print("Starting client.........")
    def print_menu(self):
        print('-------------------------------------------------')
        print ('0 -- Connectivity Check' )
        print ('1 -- add words' )
        print ('2 -- get words' )
        print ('3 -- remove words by value' )
        print ('4 -- remove words by prefix' )
        print ('5 -- add words from file' )
        print ('6 -- Quit' )
        print ('7 -- Clear screen')
    def startup_check_notification(self):
        print("Checking connectivity with server.....")
    def print_search_menu(self):
        print ('provide the search criteria')
    def add_words_menu(self):
        print('provide a comma separated list of words')
    def delete_words_menu(self):
        print('provide a comma separated list of words to delete')
    def startup_check(self, client_callback, serializer):
        self.startup_check_notification()
        serializer.serialize_connectivity()
        result = client_callback.verify_connection(serializer.trans_id, serializer.connectivity_packet)
        if(result):
            print("WE PASSED CONNECTIVITY CHECK")
            return True
        else:
            print("WE FAILED")
            return False
    def api(self, client_callback, serializer):
        while self.continue_asking:
            try:
                self.print_menu()
                selection = int(input('What would you like to do? '))
                
                if selection == 0:
                    print("Connectivity Check")
                    serializer.make_header(CONNECTIVITY_CHECK)
                    serializer.serialize_connectivity()
                    print(serializer.connectivity_packet)
                    print(serializer.packet)
                    serializer.packet = serializer.connectivity_packet
                    print(serializer.packet)
                elif selection == 1:
                    print("Add words")
                    serializer.make_header(ADD_WORDS)
                    serializer.serialize_words_add()
                    print(serializer.packet)
                elif selection == 2:
                    print("Get Words")
                    serializer.make_header(GET_WORDS)
                    serializer.serialize_words_get()
                    print(serializer.packet)
                elif selection == 3:
                    print("Remove words by value")
                    serializer.make_header(REMOVE_WORDS_BY_VALUE)
                    serializer.serialize_delete_words()
                    print(serializer.packet)
                elif selection ==4:
                    print("Remove words by prefix")
                    serializer.make_header(REMOVE_WORDS_BY_PREFIX)
                    serializer.serialize_delete_word_prefix()
                    print(serializer.packet)
                elif selection == 5:
                    print("Add words from file")
                    serializer.make_header(ADD_WORDS)
                    serializer.add_words_file(client_callback)
                elif selection == 6:
                    print("GOODBYTE")
                    self.continue_asking = False
                    break
                elif selection == 7:
                    system('clear')
                else:
                    print("not a recognized command")
                if( client_callback.send_req(serializer.packet, serializer.trans_id)):
                    print("Sent to server.....")
                    server_response = client_callback.receive_req()
                    print(server_response)
                    self.continue_asking = serializer.deserialize_data(server_response, client_callback)
                else:
                    print("Could not send")
            except ValueError:
                print("Try again")
                continue
            except TimeoutError:
                system('clear')
                continue
            except:
                print("Socket timed out")
                self.continue_asking = False

            
            

            
            