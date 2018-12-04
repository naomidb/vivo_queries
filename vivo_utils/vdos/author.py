from vivo_utils.vdos.VDO import VivoDomainObject

class Author(VivoDomainObject):
    def __init__(self, connection):
        self.connection = connection
        self.type = "person"
        self.category = "person"

        self.ufentity = False
        self.ufcurrententity = False

        self.n_number = None
        self.name = None
        self.first = None
        self.middle = None
        self.last = None
        self.email = None
        self.phone = None
        self.title = None
        self.overview = None
        self.geographic_focus = None
        self.orcid = None

        self.vcard = None
        self.name_id = None
        self.name_details = ['first', 'middle', 'last']
        self.details = ['email', 'phone', 'title', 'orcid']
        self.extra = ['overview', 'geographic_focus']

    def lookup(self, connection):
        params = {'Author': self}
        info = get_author_info.run(connection, **params)
        self.name = info['fullname']
        self.first = info['given']
        self.middle = info['middle']
        self.last = info['last']
        self.email = info['email']
        self.phone = info['phone']
        self.title = info['title']
        self.overview = info['overview']
        self.geographic_focus = info['geofocus']

    def combine_name(self):
        obj_name = ''
        if self.last:
            obj_name = self.last
            if self.first:
                obj_name = obj_name + ", " + self.first
                if self.middle:
                    obj_name = obj_name + " " + self.middle
            elif self.middle:
                obj_name = obj_name + ", " + self.middle
        elif self.first:
            if self.middle:
                obj_name = self.first + " " + self.middle
            else:
                obj_name = self.first
        elif self.middle:
            obj_name = self.middle

        self.name = obj_name
