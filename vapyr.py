#!/usr/bin/env python

import collections
import logging
import urllib.request
import json


class Client:

    def __init__(self, api_token, default_encoding="utf-8"):
        # Should support more authentication methods, but I've only needed
        # token thus far. Proxy support is built-in, fortunately.
        self.api_token = api_token 
        self.default_encoding = default_encoding

    def request(self, url, method='GET', data=None):
        req_url = url + "?private_token=%s" % (self.api_token)
        logging.debug("(%s) %s" % (method, url))
        logging.debug("Data: %s" % data)
        req = urllib.request.Request(req_url, data=json.dumps(data).encode(self.default_encoding), method=method, headers={'content-type': 'application/json'})
        try:
            with urllib.request.urlopen(req) as f:
                return json.loads(f.read().decode(self.default_encoding))
        except urllib.error.HTTPError as ex:
            logging.error("Invalid request (code: %s): %s %s" % (ex.getcode(), method, url))
            if data:
                logging.error("Data: %s" % (json.dumps(data, indent=2)))
            return []


# A somewhat ugly hack in the name of syntatic sugar.
# Since running api.projects[project_id].messages returns a DICT and DICTs
# don't support "post" method, we wrap the standard dict class. This allows
# us to write: api.projects[project_id].messages.post({'x': 'new_message'})
# Apart from supporting POST, it behaves exactly like a normal dictionary.
class ResourceContainer(collections.MutableMapping):

    def __init__(self, client, endpoint, resource_type, *args, **kwargs):
        self.client = client
        self.endpoint = endpoint
        self.resource_type = resource_type
        self.store = {}
        self.store.update(dict(*args, **kwargs))

    def __setitem__(self, key, value):
        self.store[key] = value
    def __delitem__(self, key):
        del self.store[key]
    def __iter__(self):
        return iter(self.store)
    def __len__(self):
        return len(self.store)

    def __getitem__(self, key):
        """
            In theory /projects/users returns a list of users:
                for u in projects.users: print u
            And to access bob, we would:
                print(projects.users["bob"])

            Unfortunately, they aren't always well implemented, and even
            though /projects/users/bob works, if /projects/users returns
            no results, our implementation breaks.

            This method fixes that.
        """
        if not key in self.store.keys():
            endpoint = "/".join(self.endpoint.split("/")[:-1])
            self.store[key] = self.resource_type(self.client, endpoint, {'id': key})
        return self.store[key]

    def post(self, data=None):
        """
            Enable synatic sugar.
                print(projects.users["bob"]) it works as expected.
                print(projects.users) returns a dictionary, as expected.
            But dictionaries don't have "post" methods
        """
        return self.client.request(self.endpoint, "POST", data)


class Resource:

    def __init__(self, client, parent='', attrs=None):
        self.client = client
        self.endpoint = parent
        self.attrs = attrs
        self.resources = {}
        self.cache = {}

    def __getattr__(self, name):
        if not name in self.resources.keys():
            raise AttributeError("Resource not implement or unavailable.")

        # Build up the cache if there is none
        if not name in self.cache.keys():
            self.cache[name] = ResourceContainer(self.client, self.endpoint + '/' + name, self.resources[name])
            """
                Eagerly fetch the resource (for example, /users) which will allow
                the user to iterate through the results. None given, we have to
                trust the ResourceContainer object to do what's right.
            """
            for i in self.client.request(self.endpoint + '/' + name):
                resource_instance = self.resources[name](self.client, self.endpoint, i)
                # Store the retrieved result. The requirement of that specific
                # resource identifier is currently hardcoded to "id". Perhaps
                # we could make this dynamic in the future.
                self.cache[name][i["id"]] = resource_instance

        return self.cache[name]

    def __getitem__(self, key):
        if not key in self.attrs:
            self.attrs = self.get()
        return self.attrs[key]

    def get(self):
        return self.client.request(self.endpoint)

    def post(self, data=None):
        return self.client.request(self.endpoint, "POST", data)

    def delete(self):
        return self.client.request(self.endpoint, "DELETE")

    def put(self, data=None):
        return self.client.request(self.endpoint, "PUT", data)

    def patch(self, data=None):
        return self.client.request(self.endpoint, "PATCH", data)

    def __str__(self):
        return json.dumps(self.attrs, indent=2)
