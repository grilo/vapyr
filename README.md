# vapyr
Python3-only minimalist framework to build REST clients for your favorite services. Declare your endpoints and use the API as a python dict, keeping your code clean.

## Usage

Implement the resource you wish to interface with:

```python
	#!/usr/bin/env python3

	import vapyr
	
	class GitLab(vapyr.Resource):
		def __init__(self, client, parent='', attrs={}):
		        super().__init__(client, parent, attrs)
		        self.endpoint = 'http://localhost/api/v3'
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
```	

Since the parent resources knows about its children, the instantiation happens on the fly when accessing the child resources.

Now we can use that resource by instantiating a client (only API token supported at the moment).

```python
	client = vapyr.Client('oB1H1R2jmcyNi4zGFzsJ')
	gitlab = GitLab(client)
	for project_id, project in gitlab.projects.items():
		print(project)
```

It also supports fancier stuff, such as:

```python
	project_definition = {
		'name': some_name,
		'repository:' blah_blah,
	}
	gitlab.projects.post(project_definition)
```

Everything looks like a dictionary. Another example:

```python
	# Delete all merge requests associated with a project
	for mr in gitlab.projects[1].merge_requests.values():
		mr.delete(data)
```
