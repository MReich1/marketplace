"""Übersicht über den Dateiinhalt:

Die Klasse Users verwaltet alle Benutzer des Online-Marktplatzes.
Sie erbt von `Praktikumsgruppen` und liest Benutzer- sowie Freundschaftsdaten
aus den CSV-Dateien (`user.csv`, `friends.csv`) ein. Sie stellt Methoden zur
Passwortüberprüfung, Freundschaftsempfehlung, Abstands- und Verbindungsberechnung bereit.
"""

# Status: FINAL, dgaida2, 15.10.2024

# definiert die Klasse Users.
# Users ist eine Menge von disjunkten Mengen (nur für drittes Praktikum) von der Klasse User,
# damit man Users in Praktikumsgruppen einsortieren kann. Für das erste und zweite Praktikum ist die Klasse
# Praktikumsgruppe lediglich ein Dictionary
# in der Klasse werden die csv-Dateien user.csv und friends.csv gelesen.

from typing import Any, Dict, List, Optional, Tuple, Union
import ast
import csv
import marketplace.user
import marketplace.praktikumsgruppen


class Users(marketplace.praktikumsgruppen.Praktikumsgruppen):
    """Klasse zur Verwaltung aller registrierten Benutzer und ihrer Freundschaften.

    Attributes:
        _groupnumbers (List[int]): Liste der Gruppennummern der eingelesenen Benutzer.
    """
    _map_graph = None

    @classmethod
    def get_map_graph(cls):
        """Lädt den OSMnx-Straßengraphen einmalig und speichert/lädt ihn lokal."""
        if cls._map_graph is None:
            import os
            import osmnx as ox
            graph_file = "nrw_driving_graph.graphml"
            if os.path.exists(graph_file):
                cls._map_graph = ox.load_graphml(graph_file)
            else:
                cls._map_graph = ox.graph.graph_from_address(
                    'Steinmüllerallee 1, Gummersbach, Germany', dist=50000, network_type='drive'
                )
                ox.save_graphml(cls._map_graph, graph_file)
        return cls._map_graph
    # *** CONSTRUCTORS ***
    def __init__(self, csvfile: str, *args: Any) -> None:
        """Initialisiert das Users-Objekt und liest Daten aus CSV-Dateien ein.

        Args:
            csvfile (str): Pfad zur Benutzer-CSV-Datei (z. B. 'user.csv').
            *args (Any): Variable Argumente.

        Raises:
            FileNotFoundError: Falls die CSV-Datei nicht gefunden wurde.
        """
        super().__init__()

        self._read_users_from_csvfile(csvfile)
        self._read_friends_csv('friends.csv')

        # erstelle Praktikumsgruppen als Menge disjunkter Mengen bzw. als dictionary (1. und 2. Praktikum)
        super().create_groups(list(self.keys()), self._groupnumbers)

    # *** PUBLIC SET methods ***

    # *** PUBLIC methods ***

    def add(self, user_id: str, password: str, name_family: str = "", name_first: str = "",
            gps_coord: Tuple[Optional[float], Optional[float]] = (None, None), address: str = "") -> None:
        """Adds the given user with user_id to the internal dictionary.

        Args:
            user_id (str): GM-ID / unique user identifier.
            password (str): Password of user.
            name_family (str, optional): Family name of user. Defaults to "".
            name_first (str, optional): First name of user. Defaults to "".
            gps_coord (tuple, optional): (latitude, longitude) coordinates. Defaults to (None, None).
            address (str, optional): Address string corresponding to GPS coordinates. Defaults to "".
        """
        self[user_id] = marketplace.user.User(user_id, password, name_family, name_first, gps_coord, address)

    def calc_distance_between_users(self, user_id1: str, user_id2: str) -> float:
        """Calculates distance between GPS coordinates of two users."""
        import networkx as nx
        import osmnx as ox

        user1 = self[user_id1]
        user2 = self[user_id2]
        
        coord1 = user1.gps_coords()
        coord2 = user2.gps_coords()

        if not coord1 or not coord2 or coord1[0] is None or coord2[0] is None:
            return float('inf')

        lat1, lon1 = coord1
        lat2, lon2 = coord2

        graph = Users.get_map_graph()

        origin = ox.distance.nearest_nodes(graph, lon1, lat1)
        destination = ox.distance.nearest_nodes(graph, lon2, lat2)

        try:
            shortest_path = ox.routing.shortest_path(graph, origin, destination, weight='length')
            distance_m = nx.path_weight(graph, shortest_path, weight='length')
            return float(distance_m / 1000.0)  # in Kilometern
        except (nx.NetworkXNoPath, KeyError):
            return float('inf')

    # *** PUBLIC GET methods ***

    def get_name_of_user(self, user_id: str) -> str:
        """Gibt den vollständigen Namen des Benutzers zurück.

        Args:
            user_id (str): Benutzer-ID.

        Returns:
            str: Name des Benutzers.

        Raises:
            KeyError: Falls die `user_id` nicht existiert.
        """
        node = self[user_id]
        return node.name()

    def num_users(self) -> int:
        """Gibt die Gesamtanzahl registrierter Benutzer zurück.

        Args:
            None

        Returns:
            int: Anzahl der Benutzer.

        Raises:
            None
        """
        return len(self.keys())

    def password_valid(self, user_id: str, password: str) -> bool:
        """Prüft, ob das Passwort für den angegebenen Benutzer gültig ist.

        Args:
            user_id (str): Benutzer-ID.
            password (str): Passwort.

        Returns:
            bool: `True`, wenn Passwort korrekt, sonst `False`.

        Raises:
            KeyError: Falls die `user_id` nicht existiert.
        """
        return self[user_id].password_valid(password)

    def get_user_pretty_print_for_list(self, user_id: str) -> str:
        """Erstellt eine formatierte Repräsentation eines Benutzers für Listboxen.

        Args:
            user_id (str): Benutzer-ID.

        Returns:
            str: Der formatierte Benutzer-String inkl. Praktikumsgruppen-Info.

        Raises:
            KeyError: Falls `user_id` nicht existiert.
        """
        return (self[user_id].pretty_print() + "\t in Praktikumsgruppe repräsentiert durch: " +
                str(self.find_byid(user_id, True)))

    def get_friends_andgroupmembers_pretty_print(self, user_id: str) -> List[str]:
        """Returns list of friends and group members for the given user_id that is shown on GUI.

        Args:
            user_id (str): usually the current user id

        Returns:
            List[str]: Liste formatierter Strings.

        Raises:
            KeyError: Falls `user_id` nicht existiert.
        """
        friends = self[user_id].friends()
        friend_names = [self.get_user_pretty_print_for_list(friend) for friend in friends]

        group_members = self.get_groupmembers(user_id)
        if group_members is None:
            return friend_names

        # entferne mich selbst aus der Gruppe, da ich ja weiß, dass ich (user_id) in der Gruppe bin
        if user_id in group_members:
            group_members.remove(user_id)

        group_members_pp = [self.get_user_pretty_print_for_list(member) for member in group_members]
        return friend_names + group_members_pp

    def get_mutual_friends(self, user_id: str) -> Dict[str, int]:
        """Ermittelt gemeinsame Freunde (Freunde von Freunden) und deren Häufigkeit.

        Args:
            user_id (str): usually the current user id

        Returns:
            Dict[str, int]: dictionary with friends of the friends of given user_id together with the information with how many friends of user_id these friends are friends with

        Raises:
            KeyError: Falls `user_id` nicht existiert.
        """
        friends = self[user_id].friends()
        mutual_friends_count: Dict[str, int] = {}

        for friend in friends:
            friend_friends = self[friend].friends()
            for mutual_friend in friend_friends:
                if mutual_friend != user_id and mutual_friend not in friends:
                    if mutual_friend in mutual_friends_count:
                        mutual_friends_count[mutual_friend] += 1
                    else:
                        mutual_friends_count[mutual_friend] = 1

        return mutual_friends_count

    def suggest_friends(self, user_id: str, num_common_friends: int = 2,
                        distance_threshold: float = 0.1, pretty_print: bool = True) -> List[str]:
        """Suggests users to the given user_id..."""
        if user_id not in self:
            raise KeyError(f"User {user_id} does not exist.")

        user_friends = set(self[user_id].friends())
        mutual_friends_count = self.get_mutual_friends(user_id)

        common_candidates = [
            (uid, count) for uid, count in mutual_friends_count.items()
            if count >= num_common_friends and uid not in user_friends and uid != user_id
        ]
        common_candidates.sort(key=lambda x: x[1], reverse=True)
        part1_users = [uid for uid, _ in common_candidates]
        part1_set = set(part1_users)

        nearby_candidates = []
        for other_id in self.keys():
            if other_id == user_id or other_id in user_friends or other_id in part1_set:
                continue

            if self.are_users_connected(user_id, other_id, degree=3):
                dist = self.calc_distance_between_users(user_id, other_id)
                if dist < distance_threshold:
                    nearby_candidates.append((other_id, dist))

        nearby_candidates.sort(key=lambda x: x[1])
        part2_users = [uid for uid, _ in nearby_candidates]

        suggested_user_ids = part1_users + part2_users

        if pretty_print:
            return [self[uid].pretty_print() for uid in suggested_user_ids]

        return suggested_user_ids

    def are_users_connected(self, user_id1: str, user_id2: str, degree: int = 3) -> bool:
        """Prüft mittels Breitensuche, ob zwei Benutzer über Freundschaftskanten verbunden sind."""
        if user_id1 not in self or user_id2 not in self:
            return False
        if user_id1 == user_id2:
            return True

        from collections import deque

        queue = deque([(user_id1, 0)])
        visited = {user_id1}

        while queue:
            current_id, current_degree = queue.popleft()

            if current_degree >= degree:
                continue

            for friend_id in self[current_id].friends():
                if friend_id == user_id2:
                    return True
                if friend_id not in visited:
                    visited.add(friend_id)
                    queue.append((friend_id, current_degree + 1))

        return False

    # *** PUBLIC STATIC methods ***

    # *** PRIVATE methods ***

    def _read_users_from_csvfile(self, csvfile: str) -> None:
        """
        Read the given csvfile that contains all students that want to do the Praktikum in this semester
        including their GM-ID, Names and number of their Praktikumsgruppe

        :param csvfile: csv file that has to be created at the beginning of the semester containing all students
        in this semester
        """
        with open(csvfile, newline='', encoding='utf-8-sig') as f:
            csvreader = csv.reader(f)
            # Skip header row
            next(csvreader)

            # private member variable containing the Praktikumsgruppe number of the students in the order that the
            # students are read from the csv file
            self._groupnumbers = []

            for row in csvreader:
                user_id, name_family, name_first, password, groupnum, gps_coords, address = row
                # macht aus String wieder das Tuple mit long und lat Koordinaten
                # (literal_eval statt eval, damit aus der CSV-Datei kein beliebiger Code ausgeführt werden kann)
                gps_coords_tuple = ast.literal_eval(gps_coords)
                self.add(user_id, password, name_family, name_first, gps_coords_tuple, address)
                self._groupnumbers.append(int(groupnum))

    def _read_friends_csv(self, file_path: str) -> None:
        """
        Funktion, um die friends.csv-Datei einzulesen und ein Dictionary zu erstellen
        :param file_path: path to friends.csv file
        """
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            csvreader = csv.reader(f)
            next(csvreader)  # Überspringe die Header-Zeile
            for row in csvreader:
                user_id = row[0]
                friends = row[1].split(', ')
                self[user_id].friends_add_list(friends)
                for friend in friends:  # gehe alle Freunde durch und füge user_id ebenfalls als Freund hinzu
                    self[friend].friends_add(user_id)

    # *** PUBLIC methods to return class properties ***

    # *** PRIVATE variables ***
