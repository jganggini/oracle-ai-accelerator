import os
import ads
import oracledb
from dotenv import load_dotenv

load_dotenv()

class Connection:
    """
    Singleton class for managing a reusable Oracle database connection.

    Ensures only one instance of the connection is created and reused throughout the application.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Connection, cls).__new__(cls)
            # Persist configuration to allow seamless reconnection
            cls._instance._db_config = {
                "user": os.getenv('CON_ADB_DEV_USER_NAME'),
                "password": os.getenv('CON_ADB_DEV_PASSWORD'),
                "dsn": os.getenv('CON_ADB_DEV_SERVICE_NAME'),
                "config_dir": os.getenv('CON_ADB_WALLET_LOCATION'),
                "wallet_location": os.getenv('CON_ADB_WALLET_LOCATION'),
                "wallet_password": os.getenv('CON_ADB_WALLET_PASSWORD')
            }
            cls._instance.conn = cls._instance._create_connection()
        return cls._instance

    def _create_connection(self):
        """
        Create a new database connection using the stored configuration.
        """
        conn = oracledb.connect(
            user=self._db_config["user"],
            password=self._db_config["password"],
            dsn=self._db_config["dsn"],
            config_dir=self._db_config["config_dir"],
            wallet_location=self._db_config["wallet_location"],
            wallet_password=self._db_config["wallet_password"]
        )
        conn.autocommit = True
        return conn

    def _ensure_connection(self):
        """
        Ensure the connection is alive; recreate it if it was dropped by the
        network/database (e.g., DPY-4011, timeouts, etc.).
        """
        if self.conn is None:
            self.conn = self._create_connection()
            return
        try:
            # Fast health check; raises if not connected
            self.conn.ping()
        except oracledb.Error:
            # Recreate a fresh connection on any ping failure
            try:
                self.conn.close()
            except Exception:
                pass
            self.conn = self._create_connection()

    def get_connection(self):
        """
        Returns the Oracle database connection instance.

        Returns:
            oracledb.Connection: The database connection object.
        """
        self._ensure_connection()
        return self.conn

    def close_connection(self):
        """
        Closes the Oracle database connection if it is open.
        """
        if self.conn is not None:
            try:
                self.conn.close()
                self.conn = None
            except oracledb.DatabaseError as e:
                error, = e.args
                print(f"Error closing the database connection: {error.message}")
                raise

    def __enter__(self):
        """
        Enables the use of the class in a context manager (with statement).

        Returns:
            Connection: The current instance of the connection class.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Ensures the connection is closed when exiting the context.
        """
        self.close_connection()