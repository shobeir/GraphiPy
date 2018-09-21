from pinterest import Pinterest


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
        self.pinterest.search_boards(keyword)

    def fetch_pinterest_pins(
        self,
        keyword,
        limit=20,
        before=0,
        after=0
    ):
        self.pinterest.search_pins(keyword)

    def fetch_pinterest_users(
        self,
        keyword,
        limit=20,
        before=0,
        after=0
    ):
        self.pinterest.search_users(keyword)

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
