#!/usr/bin/env python

import vapyr


class GitLab(vapyr.Resource):
    def __init__(self, client, parent='', attrs={}):
        super().__init__(client, parent, attrs)
        self.endpoint = 'http://ubuntu/api/v3'
        self.resources = {
            'projects': Project,
        }


class Project(vapyr.Resource):
    def __init__(self, client, parent, attrs):
        super().__init__(client, parent, attrs)
        self.endpoint += '/projects/' + str(attrs['id'])
        self.resources = {
            'merge_requests': MergeRequest,
            'statuses': Status,
        }


class MergeRequest(vapyr.Resource):
    def __init__(self, client, parent, attrs):
        super().__init__(client, parent, attrs)
        self.endpoint += '/merge_requests/' + str(attrs['id'])
        self.resources = {
            'commits': Commit,
            'notes': Note,
        }


class Commit(vapyr.Resource):
    def __init__(self, client, parent, attrs):
        super().__init__(client, parent, attrs)
        self.endpoint += '/commits/' + str(attrs['id'])


class Note(vapyr.Resource):
    def __init__(self, client, parent, attrs):
        super().__init__(client, parent, attrs)
        self.endpoint += '/notes/' + str(attrs['id'])


class Status(vapyr.Resource):
    def __init__(self, client, parent, attrs):
        super().__init__(client, parent, attrs)
        self.endpoint += '/statuses/' + str(attrs['id'])


if __name__ == '__main__':

    import random
    import logging
    log_format = '%(asctime)s::%(levelname)s::%(message)s'
    log_level = 'DEBUG'
    logging.basicConfig(format=log_format)
    logging.getLogger().setLevel(getattr(logging, log_level.upper()))

    # Example usage
    client = vapyr.Client('oB1H1R2jmcyNi4zGFzsJ')
    gitlab = GitLab(client)

    project_id = 1
    merge_request_id = 21

    for k, v in gitlab.projects[project_id].merge_requests[merge_request_id].commits.items():
        print(k, v)

    data = {
        'id': project_id,
        'merge_request_id': merge_request_id,
        'body': "A nice message!",
    }
    gitlab.projects[project_id].merge_requests[merge_request_id].notes.post(data)
