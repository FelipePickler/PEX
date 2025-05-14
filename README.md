# Barbearia System

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/barbearia-system.git
   ```
2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Initialize the database:
   ```
   python init_db.py
   ```
5. Run the application:
   ```
   flask run
   ```
   The application will be available at `http://localhost:5000/`.

## Usage

The Barbearia System provides the following features:

1. **Scheduling Appointments**: Users can schedule appointments for haircuts, beard trims, or a combination of both. The system checks for availability and prevents overbooking.
2. **Admin Panel**: The admin panel allows managing all scheduled appointments, including viewing, filtering, editing, and deleting them.
3. **Statistics**: The application provides statistics on the number of appointments per day, appointments per service, and the most popular time slots.
4. **Export Appointments**: Administrators can export all scheduled appointments to a CSV file.

## API

The Barbearia System provides the following API endpoints:

- `GET /get_agendamentos`: Returns a JSON list of all scheduled appointments.
- `GET /horarios_disponiveis/<data>`: Returns a JSON list of available time slots for a specific date.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature-name`.
3. Make your changes and commit them: `git commit -am 'Add some feature'`.
4. Push to the branch: `git push origin feature/your-feature-name`.
5. Submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Testing

The Barbearia System includes unit tests for the following functionality:

- Scheduling an appointment
- Editing an appointment
- Deleting an appointment
- Generating appointment statistics

To run the tests, use the following command:

```
pytest
```

The tests are located in the `test_agendamento.py` and `test_statistics.py` files.
