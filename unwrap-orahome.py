#!/usr/bin/python3

import os
import re
import glob
import plsql_unwrap

dest_dir = 'unwrapped'

if os.path.exists(dest_dir):
    files = glob.glob(os.path.join(dest_dir, '*'))
    for file in files:
        os.unlink(file)  # Remove the file or link
else:
    os.makedirs(dest_dir)

def extract_create_statements(file_content):
    pattern  = r"create.*?wrapped(.*?)^/$"
    return re.findall(pattern, file_content, re.IGNORECASE | re.MULTILINE | re.DOTALL)

orahome = os.getenv('ORACLE_HOME')
if orahome is None:
   print('ORACLE_HOME is not defined')
   quit()

orahome_rdbms_admin = os.path.join(orahome, 'rdbms', 'admin')


if not os.path.isdir(orahome_rdbms_admin):
   print(f'{orahome_rdbms_admin} does not exist')
   quit()

def write_file(name, content):
    sql_filename = name + '.sql'
    
    file_path = os.path.join(dest_dir, sql_filename)
    
    if os.path.exists(file_path):
       print(f'The file {sql_filename} already exists')
       return

    with open(file_path, 'w') as file:
         file.write(content)


for filename in os.listdir(orahome_rdbms_admin):
    if filename.endswith('.plb'):
#      print(filename)
       plbfilepath = os.path.join(orahome_rdbms_admin, filename)

       with open(plbfilepath, 'r') as plbfile:
            plbfiletext = plbfile.read()

            for create_statement in extract_create_statements(plbfiletext):
                unwrapped = plsql_unwrap.unwrap(create_statement)

                unwrapped_first_line = unwrapped.split('\n')[0]
#               print('  ' + unwrapped_first_line)
                pattern = r'(?:PACKAGE|TYPE|LIBRARY|PROCEDURE|FUNCTION)( BODY)? "?([a-zA-Z0-9$#_]+)"?(( TRUSTED)? (AUTHID DEFINER )?[AI]S)?'
                match = re.search(pattern, unwrapped_first_line)
                object_name = match.group(2)

                if object_name == None:
                #  Should not happen.
                   print(plbfilepath)
                   print(unwrapped_first_line)
                   quit()

                if match.group(1) != None:
                   object_name = f'{object_name}-{match.group(1).strip()}'.lower()


                write_file(object_name, unwrapped)
