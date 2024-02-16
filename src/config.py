from sqlalchemy import URL

class Config:
    # Secret
    SECRET_KEY = "dev"

    # Database
    DB_DRIVER = "postgresql"
    DB_HOST = "db"
    DB_NAME = "postgres"
    DB_USER = "postgres"
    DB_PASS = "password"
    DB_PORT = 5432

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return URL.create(
            drivername=self.DB_DRIVER,
            username=self.DB_USER,
            password=self.DB_PASS,
            host=self.DB_HOST,
            database=self.DB_NAME,
            port=self.DB_PORT,
        )