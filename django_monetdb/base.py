from django.db.backends import *
from django.conf import settings

import monetdb.sql as Database

from django_monetdb.introspection import DatabaseIntrospection
from django_monetdb.creation import DatabaseCreation

DatabaseError = Database.DatabaseError
IntegrityError = Database.IntegrityError

class DatabaseWrapper(BaseDatabaseWrapper):
    """
    Represents a database connection.
    """

    ops = None

    def __init__(self, settings_dict):
        super(DatabaseWrapper, self).__init__(settings_dict)

        # `settings_dict` should be a dictionary containing keys such as
        # DATABASE_NAME, DATABASE_USER, etc. It's called `settings_dict`
        # instead of `settings` to disambiguate it from Django settings
        # modules.
        #self.connection = None
        #self.queries = []
        #self.settings_dict = settings_dict

        self.features = DatabaseFeatures()
        self.ops = DatabaseOperations()
        self.validation = BaseDatabaseValidation()
        self.introspection = DatabaseIntrospection(self)
        self.creation = DatabaseCreation(self)

    def _cursor(self):
	kwargs = {}
        if not self.connection:
            if settings.DATABASE_USER:
                kwargs['username'] = settings.DATABASE_USER
            if settings.DATABASE_NAME:
                kwargs['database'] = settings.DATABASE_NAME
            if settings.DATABASE_PASSWORD:
                kwargs['password'] = settings.DATABASE_PASSWORD
            self.connection = Database.connect(**kwargs)
        return self.connection.cursor()

class DatabaseFeatures(BaseDatabaseFeatures):

    #
    # I'm not sure about this one.  If MonetDB can select from a table
    # it's updating, then we can leave this as the default of True.
    # Setting it to False is slower but will always work.  See
    # Django's source file db/models/sql/subqueries.py for the only place
    # this is used.
    #

    update_can_self_select = False

    #
    # Again, I'm not sure about this, so I'll use the more conservative
    # settings.
    #
    # Here's a relevant comment from the only file that uses this setting:
    # db/models/fields/related.py:
    #
    #     The database column type of a ForeignKey is the column type
    #     of the field to which it points. An exception is if the
    #     ForeignKey points to an AutoField / PositiveIntegerField /
    #     PositiveSmallIntegerField, in which case the column type
    #     is simply that of an IntegerField.  If the database needs
    #     similar types for key fields however, the only thing we can
    #     do is making AutoField an IntegerField.
    #

    related_fields_match_type = False

class DatabaseOperations(BaseDatabaseOperations):
    """
    This class encapsulates all backend-specific differences, such as the way
    a backend performs ordering or calculates the ID of a recently-inserted
    row.
    """

    def quote_name(self, name):
	'''Return quoted name of table, index or column name.'''
        if name.startswith('"') and name.endswith('"'):
            return name 
	return name
        #return '"%s"' % (name,)
