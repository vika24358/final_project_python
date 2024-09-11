from abc import ABC, abstractmethod
import sqlite3

from fastapi import HTTPException, status

from schemas import NewTour, SavedTour, DeletedTour


class BaseStorageTour(ABC):
    @abstractmethod
    def create_tour(self, new_tour: NewTour):
        pass

    @abstractmethod
    def get_tour(self, _id: int):
        pass

    @abstractmethod
    def get_tours(self, limit: int):
        pass

    @abstractmethod
    def update_tour_price(self, _id: int, new_price: float):
        pass

    @abstractmethod
    def delete_tour(self, _id: int):
        pass


class StorageSQLite(BaseStorageTour):

    def _create_table(self):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            query = f"""
                CREATE TABLE IF NOT EXISTS {self.tours_table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    description TEXT,
                    price REAL,
                    cover TEXT,
                    destination TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP 
                )
            """
            cursor.execute(query)

    def __init__(self, database_name):
        self.database_name = database_name
        self.tours_table_name = 'tours'
        self._create_table()

    def create_tour(self, new_tour: NewTour):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            values = (new_tour.title, new_tour.description, new_tour.price, str(new_tour.cover), new_tour.destination)
            query = f"""
                INSERT INTO {self.tours_table_name} (title, description, price, cover, destination)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query, values)

        return self._get_latest_tour()

    def _get_latest_tour(self) -> SavedTour:
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            query = f"""
                SELECT id, title, description, price, cover, destination, created_at
                FROM {self.tours_table_name}
                ORDER BY id DESC
                LIMIT 1

            """
            result = cursor.execute(query).fetchone()
            id, title, description, price, cover, destination, created_at = result
            saved_tour = SavedTour(
                id=id, title=title, description=description, price=price, cover=cover, destination=destination,
                created_at=created_at
            )

            return saved_tour

    def get_tour(self, _id: int):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            query = """
                    SELECT id, title, description, price, cover, destination, created_at
                    FROM tours
                    WHERE id = ?
                    LIMIT 1
                    """
            result = cursor.execute(query, (_id,)).fetchone()
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Oops! It seems like tour with {_id} does not exist, please check again!')
        id, title, description, price, cover, destination, created_at = result
        saved_tour = SavedTour(
            id=id, title=title, description=description, price=price, cover=cover, destination=destination,
            created_at=created_at
        )

        return saved_tour

    def get_tours(self, limit: int = 10, q: str = ""):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            query = f"""
            SELECT id, title, description, price, cover, destination, created_at
            FROM {self.tours_table_name}
            WHERE title LIKE '%{q}%' OR description LIKE '%{q}%' OR destination LIKE '%{q}%'
            LIMIT {limit}
            """
        data: list[tuple] = cursor.execute(query).fetchall()
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Oops! It seems like tours like this do not exist, please try again!')
        list_of_tours = []
        for tour in data:
            id, title, description, price, cover, destination, created_at = tour
            saved_tour = SavedTour(
                id=id, title=title, description=description, price=price, cover=cover, destination=destination,
                created_at=created_at
            )
            list_of_tours.append(saved_tour)
        return list_of_tours

    def update_tour_price(self, _id: int, new_price: float) -> SavedTour:
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            query = f"""
            UPDATE tours 
            SET 
                price = :Price
            WHERE id = :Id
            """
            result = cursor.execute(query, {'Id': _id, 'Price': new_price})
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f'Oops! It seems like tour with id {_id} does not exist, please try again!')
        saved_result = self.get_tour(_id)
        return saved_result

    def delete_tour(self, _id: int):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            query = f"""
                    DELETE FROM {self.tours_table_name}
                    WHERE id = :Id
                    """
            result = cursor.execute(query, {'Id': _id})
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f'Oops! It seems like tour with id {_id} does not exist, please try again!')


storage = StorageSQLite('tours_db.sqlite')
