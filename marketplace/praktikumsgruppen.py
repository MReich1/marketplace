from typing import Any, List, Optional, Union
class SetNode:
    def __init__(self) -> None:
        self._parent: SetNode = self
        self._weight: int = 1

    def parent(self) -> 'SetNode':
        return self._parent

    def weight(self) -> int:
        return self._weight

class Praktikumsgruppen(dict):
    """Klasse zur Repräsentation einer Sammlung disjunkter Mengen (Praktikumsgruppen)."""

    def __init__(self) -> None:
        super().__init__()

    # *** PUBLIC methods ***

    def find(self, node: SetNode) -> SetNode:
        """Findet die Wurzel der Menge mit Pfadverkürzung (Path Compression)."""
        if node._parent != node:
            node._parent = self.find(node._parent)  # Rekursive Pfadverkürzung
        return node._parent

    def find_byid(self, user_id: str, return_id: bool = False) -> Union[Any, str]:
        """Findet die Wurzel der Praktikumsgruppe eines Benutzers anhand seiner ID."""
        if user_id not in self:
            raise KeyError(f"Benutzer {user_id} existiert nicht.")

        node = self[user_id]
        root_node = self.find(node)

        if return_id:
            # Sucht die zugehörige ID zur Wurzel
            for uid, u_node in self.items():
                if u_node == root_node:
                    return uid
        return root_node

    def union(self, user_id1: str, user_id2: str) -> None:
        """Führt zwei Mengen mittels Weighted Quick-Union zusammen."""
        root1 = self.find_byid(user_id1)
        root2 = self.find_byid(user_id2)

        # Finde die tatsächlichen SetNode-Instanzen (falls root1/root2 Objekte sind)
        root_node1 = root1 if isinstance(root1, SetNode) else self[root1]
        root_node2 = root2 if isinstance(root2, SetNode) else self[root2]

        if root_node1 != root_node2:
            # Weighted Quick-Union: Hänge den kleineren Baum an den größeren
            if root_node1._weight < root_node2._weight:
                root_node1._parent = root_node2
                root_node2._weight += root_node1._weight
            else:
                root_node2._parent = root_node1
                root_node1._weight += root_node2._weight

    def create_groups(self, user_ids: List[str], groupnumbers: List[int]) -> None:
        """Erstellt Gruppen basierend auf den IDs und verbindet entsprechende Partner."""
        # Hinweis: Je nach genauer Aufgabenstellung im Praktikum werden hier
        # entweder alle als Singletons initialisiert oder direkt über Gruppennummern verbunden.
        # Hier werden Einträge verknüpft, die dieselbe Gruppennummer haben:
        group_mapping = {}
        for uid, gnum in zip(user_ids, groupnumbers):
            if gnum not in group_mapping:
                group_mapping[gnum] = []
            group_mapping[gnum].append(uid)

        # Verbinde alle Nutzer mit derselben Gruppennummer via union
        for gnum, members in group_mapping.items():
            if members:
                first = members[0]
                for other in members[1:]:
                    self.union(first, other)

    # *** PUBLIC GET methods ***

    def get_groupmembers(self, user_id: str) -> List[str]:
        """Gibt eine Liste aller Gruppenmitglieder der Gruppe des Benutzers zurück."""
        if user_id not in self:
            raise KeyError(f"Benutzer {user_id} existiert nicht.")

        target_root = self.find(self[user_id])
        members = []

        for uid, node in self.items():
            if self.find(node) == target_root:
                members.append(uid)

        return members

    def print_ds(self) -> None:
        """Gibt die Disjoint-Set-Struktur aus."""
        for user_id, user in self.items():
            print(user_id, self.find_byid(user_id, return_id=True))