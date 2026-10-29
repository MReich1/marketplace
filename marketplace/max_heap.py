"""Übersicht über den Dateiinhalt:

Implementiert den MaxHeap zur effizienten Verwaltung von Auktionen basierend
auf der Anzahl der abgegebenen Gebote. Die Auktion mit den meisten Geboten
befindet sich an der Spitze des Heaps.
"""

# Status: FINAL, dgaida2, 15.10.2024

# Die Klasse MaxHeap implementiert einen Max-Heap

# TODO: Diese Klasse implementieren Sie in Praktikum 2

from typing import Any, Dict, List, Optional, Tuple


class MaxHeap:
    """Klasse zur Repräsentation eines Max-Heaps für Auktionen.

    Attributes:
        heap (List[Tuple[int, str]]): Liste von (bid_count, auction_id) Tupeln.
        auction_map (Dict[str, Tuple[int, int]]): Hash-Map (auction_id -> (bid_count, heap_index)).
    """

    def __init__(self) -> None:
        """Initialisiert eine neue MaxHeap-Instanz.

        Args:
            None

        Raises:
            None
        """
        """ Initialisierung des Max-Heaps.
            Ein Knoten speichert die Anzahl der Bieter für eine Auktion sowie die ID-Nummer der Auktion.
            Die Auktion mit den meisten Bietern soll an der Spitze des Max-Heaps stehen.

        heap: Eine Liste zur Speicherung des Heaps, bestehend aus Tupeln in der Form (bid_count, auction_id).
        auction_map: Eine Hash-Map, welche die Position der Auktionen im Max-Heap speichert.
                     (key = auction_id, value = (bid_count, heap_index))
        """
        self.heap: List[Tuple[int, str]] = []
        self.auction_map: Dict[str, Tuple[int, int]] = {}
        # TODO: wenn Sie die anderen Methoden implementiert haben, können Sie diese Zeile auskommentieren
        #raise NotImplementedError

    # *** PUBLIC methods ***

    def add_auction(self, auction_id: str, bid_count: int) -> None:
        """Fügt eine neue Auktion zum Max-Heap hinzu.

        Args:
            auction_id (str): Auktions-ID.
            bid_count (int): Gebotsanzahl.

        Returns:
            None

        Raises:
            ValueError: Wenn die Auktion bereits im Heap existiert.
        """


        if auction_id in self.auction_map:
            raise ValueError("Auktion existiert bereits")
        #ans ende der heapliste anhängen
        self.heap.append((bid_count, auction_id))
        index = len(self.heap) - 1
        #in der map registrieren
        self.auction_map[auction_id] =(bid_count,index)
        #nach oben wandern lassen bis die heap-ordnung stimmt
        self._heapify_up(index)

        #nicht notwendig aber interessant:
        #Laufzeiten : Worst-case O(logn) bei hinzufügen.
        #Grund : append ist O(1) _heapify_up steigt maximal die höhe des Baumes (logn).

        #TODO:
        #raise NotImplementedError

    def update_bidders(self, auction_id: str, new_bid_count: int) -> None:
        """Aktualisiert die Gebotsanzahl einer existierenden Auktion im Heap.

        Args:
            auction_id (str): Auktions-ID.
            new_bid_count (int): Neue Gebotsanzahl.

        Returns:
            None

        Raises:
            ValueError: Wenn die Auktion nicht im Heap existiert.
        """
        if auction_id not in self.auction_map:
            raise ValueError("Auktion existiert nicht")
        #bisheriger index und wert aus map holen
        old_bid_count, index = self.auction_map[auction_id]
        #im heap und in der map mit dem neuen wert aktualisieren
        self.heap[index] = (new_bid_count,auction_id)
        self.auction_map[auction_id] = (new_bid_count,index)
        #wert gestiegen oder gefallen , reparieren
        if(new_bid_count > old_bid_count):
            self._heapify_up(index)
        if(new_bid_count < old_bid_count): #bsp gebot wird storniert
            self._heapify_down(index)

        # TODO:
        #raise NotImplementedError

    def remove(self, auction_id: str) -> None:
        """Entfernt eine Auktion aus dem Max-Heap.

        Args:
            auction_id (str): Auktions-ID.

        Returns:
            None

        Raises:
            ValueError: Wenn die Auktion nicht im Heap existiert.
        """
        if auction_id not in self.auction_map:
            raise ValueError("Auktion existiert nicht")

        #index aus der map holen O(1)
        _,index = self.auction_map[auction_id]
        last_index = len(self.heap) -1

        if(index != last_index):
            self._swap(index,last_index)
        #element hinten entfernen und aus der map löschen
        self.heap.pop()
        del self.auction_map[auction_id]
        # wenn der getauschte knoten noch im heap ist, die position korrigieren
        if(index < len(self.heap)):
            self._heapify_down(index)
            self._heapify_up(index)


        # TODO:
        #raise NotImplementedError

    def get_auction_with_max_bidders(self) -> Optional[Tuple[int, str]]:
        """Gibt die Auktion mit den meisten Geboten an der Spitze des Heaps zurück.

        Args:
            None

        Returns:
            Optional[Tuple[int, str]]: Tupel aus (bid_count, auction_id) oder `None`.

        Raises:
            None
        """
        if not self.heap:
            return None
        return self.heap[0][0], self.heap[0][1]

    def get_auction_bidders(self, auction_id: str) -> Optional[int]:
        """Gibt die Gebotsanzahl einer Auktion zurück.

        Args:
            auction_id (str): Auktions-ID.

        Returns:
            Optional[int]: Gebotsanzahl oder `None`, falls nicht vorhanden.

        Raises:
            None
        """
        if auction_id in self.auction_map:
            return self.auction_map[auction_id][0]
        return None

    # *** PRIVATE methods ***

    def _swap(self, i: int, j: int) -> None:
        """ Hilfsfunktion zum Tauschen von zwei Auktionen im Max-Heap.
            Aktualisiert ebenfalls die Position der Auktionen in der auction_map.

        Args:"""
            #i: Index der ersten Auktion im Max-Heap.
            #j: Index der zweiten Auktion im Max-Heap.

        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        count_i, id_i = self.heap[i]
        count_j, id_j = self.heap[j]

        self.auction_map[id_i] = (count_i, i)
        self.auction_map[id_j] = (count_j, j)
        # TODO:
        #raise NotImplementedError

    def _heapify_up(self, index: int) -> None:
        """ Führt das Heapify-Up-Verfahren durch, um die Heap-Eigenschaft nach oben hin wiederherzustellen.

        Args:
            index: Der Index des Elements, das nach oben "heapified" werden soll.
        """
        while(index > 0):
            parent = (index - 1) // 2
            if( self.heap[index][0] > self.heap[parent][0]):
                self._swap(index, parent)
                index = parent
            else:
                break
        # TODO:
        #raise NotImplementedError

    def _heapify_down(self, index: int) -> None:
        """ Führt das Heapify-Down-Verfahren durch, um die Heap-Eigenschaft nach unten hin wiederherzustellen.

        Args:
            index: Der Index des Elements, das nach unten "heapified" werden soll.
        """
        n = len(self.heap)

        while True:
            left = 2 * index + 1 #left child
            right = 2 * index + 2 #right child
            largest = index

            #prüft ob linkes kind exisitiert und mehr gebote hat
            if(left < n and self.heap[left][0] > self.heap[largest][0]):
                largest = left
            #prüft ob rechtes kind exisitiert und noch mehr gebote hat
            if(right < n and self.heap[right][0] > self.heap[largest][0]):
                largest = right
            # wenn kind größer: tauschen wir es
            if(largest != index):
                self._swap(index, largest)
                index = largest
            else:
                break
        # TODO:
        #raise NotImplementedError
