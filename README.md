# Banking Project

A personal financial management system that processes bank transaction data from multiple Chase accounts, stores them in PostgreSQL, and provides automated backup capabilities to AWS S3.

## Features

- **Multi-Account Support**: Process transactions from checking, savings, and credit card accounts
- **Automated Data Ingestion**: CSV-to-database pipeline with duplicate prevention
- **Change Tracking**: Audit logging for all transaction modifications
- **Automated Backups**: Local and S3-replicated database backups
- **Financial Analysis**: Categorized expense tracking and savings monitoring
- **Infrastructure as Code**: Terraform-managed AWS resources

## Project Structure

```
Banking/
├── BankingFiles_Processor/       # Main application
│   ├── main.py                   # CSV ingestion script
│   ├── backup_script.py          # Backup automation
│   ├── docker-compose.yaml       # PostgreSQL container
│   ├── sql/                      # Database schema
│   └── RawData/                  # Transaction CSV files
├── terraform/                    # AWS infrastructure
├── db_backups/                   # Local backup storage
└── pyproject.toml                # Python dependencies
```

## Prerequisites

- Docker & Docker Compose
- Python 3.12
- AWS CLI (optional, for S3 backups)

**Note**: PostgreSQL does NOT need to be installed on your host machine. The `psycopg2` library connects to PostgreSQL running in Docker via TCP/IP.

## Quick Start

### 1. Create Docker Volume

```bash
docker volume create bankingfiles_processor_banking_db-volume
```

### 2. Configure Environment

Create a `.env` file in `BankingFiles_Processor/` with the following structure:

```bash
# Database Configuration
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=banking_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5433

# Bank File Processing
BANK_FILE=./RawData/Chase9072/Chase9072_Activity_YYYYMMDD.CSV

# AWS Configuration (Optional - only needed for S3 backups)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
S3_BACKUP_BUCKET=your-backup-bucket-name
```

**Important**: Never commit `.env` to version control. Add it to `.gitignore`.

### 3. Start PostgreSQL

```bash
cd BankingFiles_Processor
docker-compose up -d
```

### 4. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install pandas psycopg2-binary python-dotenv boto3
```

### 5. Run Data Ingestion

```bash
python main.py
```

## Database Schema

### Tables

- **transactions**: Primary transaction data with categorization
- **savings**: Investment and savings account balances
- **monthly_summary**: Aggregated monthly expense data
- **change_log**: Audit trail for transaction modifications

### Supported Accounts

- Chase credit cards (Chase4659)
- Chase checking (Chase6589)
- Chase savings (Chase9072)
- Investment accounts (Webull, Vanguard)
- High-yield savings (Ally, Marcus)
- Cryptocurrency (Coinbase)

## Usage

### Import Transactions

1. Set `BANK_FILE` in `.env` to point to your CSV file
2. Run: `python main.py`

### Create Backup

```bash
python backup_script.py
```

This creates a local backup and optionally uploads to S3.

### Test Backup Restoration

```bash
bash test_backup.sh
```

### Connect to Database

```bash
docker exec -it banking_db psql -U your_username -d banking_db
```

## AWS Infrastructure

The project includes Terraform configuration for:

- S3 bucket with versioning and encryption
- IAM user with minimal permissions for backups
- Lifecycle policies (30-day Glacier transition, 90-day deletion)
- Optional SNS notifications

### Deploy Infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## Expense Categories

The system supports detailed categorization:

- **Fixed Expenses**: Rent, utilities, insurance
- **Discretionary Expenses**: Entertainment, travel
- **Variable Expenses**: Dining, shopping
- **Commute**: Transit, ride-sharing
- **Groceries**: Food shopping
- **Income**: Paycheck, reimbursements

## Architecture

The application uses a client-server architecture:

1. **Python Script** (main.py) runs on host machine
2. **psycopg2 library** connects via TCP/IP to localhost:5433
3. **Docker** maps host port 5433 to container port 5432
4. **PostgreSQL** runs inside Docker container

This design eliminates the need for PostgreSQL installation on the host.

## Security Best Practices

- Store credentials in `.env` (never commit)
- Use IAM roles instead of access keys in production
- Enable MFA on AWS account
- Rotate access keys regularly
- Enable S3 encryption (configured by default)
- Use minimal IAM permissions (configured by default)

## Troubleshooting

### Database Connection Issues

1. Verify container is running: `docker ps | grep banking_db`
2. Test port connectivity: `nc -zv localhost 5433`
3. Check environment variables in `.env`

### CSV Import Failures

1. Verify CSV format matches account type
2. Check file path in `BANK_FILE`
3. Ensure dates are in MM/DD/YYYY format

### S3 Upload Failures

1. Verify AWS credentials are configured
2. Check IAM user has PutObject permission
3. Confirm S3 bucket exists and region matches

## Dependencies

- **pandas**: CSV file processing
- **psycopg2-binary**: PostgreSQL database adapter
- **python-dotenv**: Environment variable management
- **boto3**: AWS S3 operations (optional)

## License

Private project for personal use.

## Additional Documentation

For detailed architecture documentation, see [CLAUDE.md](./CLAUDE.md).
