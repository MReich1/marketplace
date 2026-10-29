"""Übersicht über den Dateiinhalt:

Implementiert den Heap für die Bewertung von Verkäufern. Der am besten bewertete
Nutzer (höchste mittlere Sternezahl) steht an der Spitze und ist in konstanter
Zeit abrufbar. Intern wird der MaxHeap (Heap + Hashtabelle) wiederverwendet.
"""

# Status: FINAL

from typing import Optional, Tuple

from marketplace.max_heap import MaxHeap


class UserRatingHeap:
    """Max-Heap über die mittlere Sternebewertung der Nutzer.

    Die Hashtabelle des MaxHeaps (user_id -> (Bewertung, Heap-Index)) erlaubt es, einen Nutzer nach
    einer neuen Bewertung in O(1) im Heap zu finden und ihn dann in O(log n) an die richtige Stelle zu schieben.
    Ohne Hashtabelle wäre dafür eine lineare Suche in O(n) nötig.

    Attributes:
        _heap (MaxHeap): Max-Heap mit (mittlere Sterne, user_id) Einträgen.
    """

    def __init__(self) -> None:
        """Initialisiert einen leeren Bewertungs-Heap.

        Args:
            None

        Raises:
            None
        """
        self._heap: MaxHeap = MaxHeap()

    def add_user(self, user_id: str, stars_mean: float) -> None:
        """Fügt einen Nutzer mit seiner mittleren Sternebewertung hinzu.

        Args:
            user_id (str): Benutzer-ID.
            stars_mean (float): Mittlere Anzahl Sterne.

        Returns:
            None

        Raises:
            ValueError: Wenn der Nutzer bereits im Heap existiert.
        """
        self._heap.add_auction(user_id, stars_mean)

    def update_rating(self, user_id: str, stars_mean: float) -> None:
        """Aktualisiert die mittlere Sternebewertung eines Nutzers (fügt ihn hinzu, falls noch nicht vorhanden).

        Args:
            user_id (str): Benutzer-ID.
            stars_mean (float): Neue mittlere Anzahl Sterne.

        Returns:
            None

        Raises:
            None
        """
        if self._heap.get_auction_bidders(user_id) is None:
            self._heap.add_auction(user_id, stars_mean)
        else:
            self._heap.update_bidders(user_id, stars_mean)

    def remove_user(self, user_id: str) -> None:
        """Entfernt einen Nutzer aus dem Heap.

        Args:
            user_id (str): Benutzer-ID.

        Returns:
            None

        Raises:
            ValueError: Wenn der Nutzer nicht im Heap existiert.
        """
        self._heap.remove(user_id)

    def get_top_user(self) -> Optional[Tuple[float, str]]:
        """Gibt den am besten bewerteten Nutzer in konstanter Zeit zurück.

        Args:
            None

        Returns:
            Optional[Tuple[float, str]]: Tupel (mittlere Sterne, user_id) oder `None`, falls der Heap leer ist.

        Raises:
            None
        """
        return self._heap.get_auction_with_max_bidders()

    def get_rating(self, user_id: str) -> Optional[float]:
        """Gibt die gespeicherte mittlere Sternebewertung eines Nutzers zurück.

        Args:
            user_id (str): Benutzer-ID.

        Returns:
            Optional[float]: Mittlere Sterne oder `None`, falls der Nutzer nicht im Heap ist.

        Raises:
            None
        """
        return self._heap.get_auction_bidders(user_id)