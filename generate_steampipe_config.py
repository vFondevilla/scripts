import os
from google.auth import default
from googleapiclient.discovery import build

def list_gcp_projects():
    credentials, _ = default()
    service = build('cloudresourcemanager', 'v1', credentials=credentials)
    request = service.projects().list()
    projects = []
    
    while request is not None:
        response = request.execute()
        projects.extend(response.get('projects', []))
        request = service.projects().list_next(previous_request=request, previous_response=response)
    
    return projects

def sanitize_project_name(project_id):
    return project_id.replace(' ', '_').replace('-', '_')

def write_gcp_connections_file(projects, filename):
    with open(filename, 'w') as f:
        f.write('connection "gcp_all" {\n')
        f.write('  type        = "aggregator"\n')
        f.write('  plugin      = "gcp"\n')
        f.write('  connections = ["' + '", "'.join([f"gcp_project_{sanitize_project_name(project['projectId'])}" for project in projects]) + '"]\n')
        f.write('}\n\n')
        
        for project in projects:
            sanitized_project_id = sanitize_project_name(project['projectId'])
            f.write(f'connection "gcp_project_{sanitized_project_id}" {{\n')
            f.write('  plugin  = "gcp"\n')
            f.write(f'  project = "{project["projectId"]}"\n')
            f.write('}\n\n')

def main():
    projects = list_gcp_projects()
    write_gcp_connections_file(projects, 'gcp.spc')

if __name__ == '__main__':
    main()
