from pinterest import Pinterest
import pandas as pd

class Pinterest:
    def __init__(self, api):
        self.pinterest = Pinterest(
            username_or_email=api["username_or_email"],
            password=api["password"],
        )
        self.pinterest.login()

    def fetch_pinterest_boards(
        self,
        keyword,
        limit=20,
        before=0,
        after=0
    ):
        board_nodes = []
        user_nodes = []
        board_user_edges = []
        boards_result = self.pinterest.search_boards(keyword)
        for board in boards_result:
            board_node = {'id': board['id'],
                          'name': board['name'],
                          'description': board['description'],
                          'pin_count': board['pin_count']
                          }
            user_node = {'id': board['owner']['id'],
                         'username': board['owner']['username'],
                         'full_name': board['owner']['full_name']
                        }
            board_nodes.append(board_node)
            user_nodes.append(user_node)
            board_user_edges.append('Source': board['id'],
                                   'Target': board['owner']['id'])

        board_nodes_df = pd.DataFrame(board_nodes)
        board_user_edges_df = pd.DataFrame(board_user_edges)
        user_nodes_df = pd.DataFrame(user_nodes)
        board_nodes_df.to_csv("1.csv", encoding='UTF-8', index=False)
        board_user_edges_df.to_csv("2.csv", encoding='UTF-8', index=False)
        user_nodes_df.to_csv("3.csv", encoding='UTF-8', index=False)


    def fetch_pinterest_pins(
        self,
        keyword,
        limit=20,
        before=0,
        after=0
    ):
        pin_nodes = []
        board_nodes = []
        user_nodes = []
        pin_board_edges = []
        pin_user_edges = []
        pins_result = self.pinterest.search_pins(keyword)
        for pin in pins_result:
            pin_node = {'id' : pin['id'],
                        'name': pin['rich_summary']['display_name'],
                        'description': pin['rich_summary']['display_description'],
                        'created_at': pin['created_at']
                        }
            board_node = {'id' : pin['board']['id'],
                          'name': pin['board']['name'].
                        }
            user_node = user_node = {'id': pin['pinner']['id'],
                        'username': pin['pinner']['username']
                        }
            pin_nodes.append(pin_node)
            board_nodes.append(board_node)
            user_nodes.append(user_node)
            pin_board_edges.append('Source': pin['id'],
                                   'Target': pin['board']['id'])
            pin_user_edges.append('Source': pin['id'],
                                  'Target': pin['pinner']['id'])
        
        pin_nodes_df = pd.DataFrame(pin_nodes)
        pin_board_edges_df = pd.DataFrame(pin_board_edges)
        board_nodes_df = pd.DataFrame(board_nodes)
        user_nodes_df = pd.DataFrame(user_nodes)
        pin_user_edges_df = pf.DataFrame(pin_user_edges)
        pin_nodes_df.to_csv("1.csv", encoding='UTF-8', index=False)
        pin_board_edges_df.to_csv("2.csv", encoding='UTF-8', index=False)
        board_nodes_df.to_csv("3.csv", encoding='UTF-8', index=False)
        user_nodes_df.to_csv("4.csv", encoding='UTF-8', index=False)
        pin_user_edges_df.to_csv("5.csv", encoding='UTF-8', index=False)

    def fetch_pinterest_users(
        self,
        keyword,
        limit=20,
        before=0,
        after=0
    ):
        user_nodes = []
        users_result = self.pinterest.search_users(keyword)
        for user in users_result:
            user_node = {'id' : user['id'],
                        'name': user['username'],
                        'full_name': user['full_name']
            user_nodes.append(user_node)
        
        user_nodes_df = pd.DataFrame(user_nodes)
        user_nodes_df.to_csv("1.csv", encoding='UTF-8', index=False)
        
            
    def export_data(
        self,
        format,
        object_type_list,
        file_name,
        options=None
    ):
        pass


# Node class
class User (BareboneNode):
    def __init__(
            self,
            username,
            full_name,
            date_created,
            pin_count,
            follower_count,
            board_count
    ):
        self.username = username
        self.full_name = full_name
        self.date_created = date_created
        self.pin_count = pin_count
        self.follower_count = follower_count
        self.board_count = board_count


class Pin (BareboneNode):
    def __init__(
            display_name,
            display_description,
            create_at,
            creator
    ):
        self.display_name = display_name
        self.display_description = display_description
        self.create_at = create_at
        self.creator = creator


class Board (BareboneNode):
    def __init__(
            name,
            description,
            creator,
            created_at,
            pin_count,
            section_count
    ):
        self.name = name
        self.description = description
        self.creator = creator
        self.create_at = create_at
        self.pin_count = pin_count
        self.section_count = section_count


# Edge class
class Pin_Board_Edge(BareboneEdge):
    def __init__(
            self,
            pin_id,
            board_id
    ):
        BareboneEdge.__init__(self, pin_id, board_id)
