# Simcoe County Search Processor

This app processes the data behind the search component of our NodeJS [WebApi](https://github.com/county-of-simcoe-gis/SimcoeCountyWebApi).
It accepts WFS urls as the data source. This would then be scheduled to run overnight.

\*\* This is still a work in progress and will be adjusted when pushed to production.

Please visit our deployment guide for full details: https://github.com/county-of-simcoe-gis/SimcoeCountyDeploymentGuide

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

The script to create the table is part of your WebApi project: https://github.com/county-of-simcoe-gis/SimcoeCountyWebApi/blob/master/sqlScript.sql

### Prerequisites

```
Postgres
Python (Tested and Working using 2.7)
```

### Installing (using VS Code)

```
git clone https://github.com/county-of-simcoe-gis/SimcoeCountySearchProcessor.git
cd SimcoeCountySearchProcessor
F5 (Debug)
```

## Deployment

You would run the main.py like any other python file. "Path to Your Python Exe" main.py

## Built From Scratch

## Authors

-   **Al Proulx** - _Initial work_ - [Al Proulx](https://github.com/iquitwow)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
