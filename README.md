# Institute API

A Flask API for managing institutes, employees, and students. This API allows institutes to invite their employees and students, who can then register using a token. The institute can manage its employees, and employees can have profiles that perform various roles, including managing the students. It is designed as an educational institution management system.

## Features

- Institute management
  - Create, update, and delete institutes
  - Invite employees and students
  - Manage employees and their roles
- Employee management
  - Create, update, and delete employee profiles
  - Assign roles and permissions
- Student management
  - Register students using an invite token
  - Update student information
- Authentication and authorization
  - Token-based authentication
  - Role-based access control

## Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/your-username/institute-api.git
   cd institute-api
   ```

2. Create and activate a virtual environment:

   ```shell
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the required packages:

   ```shell
   pip install -r requirements.txt
   ```

4. Set up the database:

   - Make sure you have a PostgreSQL server running.
   - Create a new PostgreSQL database for the API.

   ```shell
   psql -U your_username -c "CREATE DATABASE api"
   ```

## Usage

To start the API, run the following command:

```shell
export FLASK_APP=api
flask setup_api_database
python3 api.py
```

The API will be available at `http://localhost:5000`.

![](https://github.com/jbrun0r/assets/blob/main/institute-api.gif?raw=true)

## API Endpoints

The API provides the following endpoints:

- `/auth` - Authentication endpoints
- `/document` - Document operations endpoints
- `/employee` - Employee management endpoints
- `/error` - API Error management endpoints
- `/institute` - Institute management endpoints
- `/student` - Student management endpoints
- `/user` - User management endpoints

Please refer to the API documentation or Postman collection for detailed information about the available endpoints, request payloads, and responses.

## Credits

The Institute API is developed and maintained by João Bruno.
