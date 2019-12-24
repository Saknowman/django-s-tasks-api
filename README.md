# django-s-tasks-api

**django-s-tasks-api** is a simple task and group task rest api of django.

## Installation
To install django-s-tasks-api like this:
```shell script
pip install django-s-tasks-api 
```

## Configuration
We need to hook **django-s-tasks-api** into our project.
1. Put s_tasks_api into your INSTALLED_APPS at settings module:
    ```python:project/settings.py
    INSTALLED_APPS = (
        ...,
        'rest_framework',
        'django_filters',
        's_tasks_api',
    )
    ```
   
2. Create **s_tasks_api** database table by running:
    ```shell script
    python manage.py migrate
    ```

3. Register default task status refer to default_task_status_data.json
   
4. Add url patterns at project.urls module:
    ```python:project/urls.py
    from s_tasks_api import urls as s_tasks_api_urls

    urlpatterns = [
        ...,
        path(r'api/tasks/', include(s_tasks_api_urls))
    ]
    ```
   
   
## API
### Task Status
#### List task status
Show task status list.
 
```text
method: GET
url: /api/tasks/status/
name: s-tasks:status-list
view: s_tasks_api.views.TaskStatusViewSet
```

#### Detail task status
Show task status detail.
 
```text
method: GET
url: /api/tasks/status/<pk>
name: s-tasks:status-detail
view: s_tasks_api.views.TaskStatusViewSet
```

#### Add task status
Add task status.
Only admin user can use this.
 
```text
method: POST
url: /api/tasks/status/
parameters: 
{
    'value': 'new status'
}
name: s-tasks:status-list
view: s_tasks_api.views.TaskStatusViewSet
```   


#### Update task status
Update task status.
Only admin can use this.
 
```text
method: GET
url: /api/tasks/status/<pk>
parameters:
{
    'value': 'changed'
}
name: s-tasks:status-detail
view: s_tasks_api.views.TaskStatusViewSet
```


#### Delete task status
Delete task status.
Only admin can use this.
 
```text
method: GET
url: /api/tasks/status/<pk>
name: s-tasks:status-detail
view: s_tasks_api.views.TaskStatusViewSet
```

### Task Tags
This is almost same as Task Status API, so just change status to tags.
But Add Tags is allowed to login user not only admin.


### Tasks

#### List tasks
Show tasks list which are created by user or assigned.
This is filterable.
```text
method: GET
url: /api/tasks/
filterable_parameters: [
    'title' (contains),
    'detail' (contains),
    'due_date' (less than or equals),
    'completed',
    'status',
    'tag',
]
name: s-tasks:tasks-list
view: s_tasks_api.views.TaskViewSet
```

#### Detail tasks
Show tasks detail.
```text
method: GET
url: /api/tasks/<pk>/
name: s-tasks:tasks-detail
view: s_tasks_api.views.TaskViewSet
```


#### Add tasks
Add users task.
```text
method: POST
url: /api/tasks/
parameters: 
{
    'title': 'new_task', 
    'detail': 'task detail',
    'due_date': '2099-12-03', 
    'status': 2, 
    'tag': 1
}
name: s-tasks:tasks-list
view: s_tasks_api.views.TaskViewSet
```


#### Change task
Change tasks detail.
```text
method: PUT/PATCH
url: /api/tasks/<pk>/
parameters: 
{
    'title': 'changed', 'detail': 'changed detail',
    'due_date': '2100-10-10', 'status': 3, 'tag': 3
}
name: s-tasks:tasks-detail
view: s_tasks_api.views.TaskViewSet
```


#### Complete/Un Complete task
Complete or Un Complete task.
```text
method: PATCH
url: /api/tasks/<pk>/complete/   or   /api/tasks/<pk>/un_complete/
parameters: {}
name: s-tasks:tasks-complete   or   s-tasks:tasks-un-complete
view: s_tasks_api.views.TaskViewSet
```


### Group Tasks

#### List group tasks
Show tasks list in all user's group.
This is filterable.
```text
method: GET
url: /api/tasks/group/
filterable_parameters: [
    'title' (contains),
    'detail' (contains),
    'due_date' (less than or equals),
    'completed',
    'status',
    'tag',
    'created_by',
    'assignee',
    'group',
]
name: s-tasks:group-tasks-list
view: s_tasks_api.views.GroupTaskViewSet
```

#### Detail group tasks
Show group tasks detail.
```text
method: GET
url: /api/tasks/group/<pk>/
name: s-tasks:group-tasks-detail
view: s_tasks_api.views.GroupTaskViewSet
```

#### Add group task
Add group task.
```text
method: POST
url: /api/tasks/create_group_task/
parameters: 
{
    'title': 'new_task', 
    'detail': 'task detail',
    'due_date': '2099-12-03', 
    'status': 2, 
    'tag': 1,
    'group': 2, 
    'assignee': 2,
    'lock_level': 0, 
    'assign_lock_level': 0
}
name: s-tasks:tasks-create-group-task
view: s_tasks_api.views.TaskViewSet
```

#### Move task from user's to group's
Move task from user's to group's
```text
method: POST
url: /api/tasks/group/
parameters: 
{
    'task_id': 1,
    'group': 2, 
    'assignee': 2,
    'lock_level': 0, 
    'assign_lock_level': 0
}
name: s-tasks:group-tasks-list
view: s_tasks_api.views.GroupTaskViewSet
```


#### Update group task
Update group task.
Permission is depends on lock_level and assign_lock_level.
```text
method: PUT/PATCH
url: /api/tasks/group/<pk>/
parameters: 
{
    'title': 'changed', 
    'detail': 'changed detail',
    'due_date': '2100-10-10', 
    'status': 3, 
    'tag': 3,
    'assignee': 2,
    'lock_level': 0, 
    'assign_lock_level': 0
}
name: s-tasks:group-tasks-detail
view: s_tasks_api.views.GroupTaskViewSet
```

#### Complete/Un Complete group task
Complete and Un Complete group task.
Permission is depends on lock_level.
```text
method: PATCH
url: /api/group/tasks/<pk>/complete/   or   /api/tasks/group/<pk>/un_complete/
parameters: {}
name: s-tasks:group-tasks-complete   or   s-tasks:group-tasks-un-complete
view: s_tasks_api.views.GroupTaskViewSet
```

#### Delete group task
Delete group task with task.
```text
method: DELETE
url: /api/tasks/group/<pk>/
name s-tasks:group-tasks-detail
view: s_tasks_api.views.GroupTaskViewSet
```

#### Remove group task to user's task
Remove group task to user's task
```text
method: DELETE
url: /api/tasks/group/<pk>/remove_to_my_task/
name s-tasks:group-tasks-remove-to-my-task
view: s_tasks_api.views.GroupTaskViewSet
```
