# Analyzers [![License: LGPL v3](https://img.shields.io/badge/License-LGPL_v3-orange.svg)](COPYING.LESSER)
_Soon..._

> Version: **v1.0.0-b.0**

## Documentation
### Technician installation guide
#### Inserting new PGN files to a postgreSQL database

Create a config.json file containing the connection parameters to the postgreSQL server and the paths to the PGNFiles you wish to add. An [example](https://github.com/ShallowView/Analyzers/blob/bc15b9bebc912fdcf9aab287c73a106685f735c4/DataCollection/config.json) is present in DataCollection/

Launch the module:
``` bash
python -m DataCollection <config_file>
```

#### Generating network graphs with Louvain partitioning

Create a input.json file containing the connection parameters to the postgreSQL server and the JSON output path. An [example](https://github.com/ShallowView/Analyzers/blob/987ff18241b36f8aa059fa75a3895d0925b9144c/Louvain/input.json) is present in Louvain/

Launch the module:
``` bash
python -m Louvain -c <color> -l <layout> <config_file>
```

For additional options, you can use the help command:
``` bash
python -m Louvain -h
```

### Developer preparation guide
_Soon..._

## License
Analyzers (Python modules)  
Copyright &copy; 2025 - ShallowView (https://www.shallowview.fr/)

These programs is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

The latters are distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU General Public License and the GNU
Lesser General Public License along with the programs (Links:
[GNU GPL v3](COPYING) & [GNU LGPL v3](COPYING.LESSER)). If not, see
https://www.gnu.org/licenses/.

## Developers
> [Adrien Gueguen](https://github.com/agueguen-LR) (Database Engineer)

> [Ndeye659](https://github.com/Ndeye659) (Data Analyst)

> [SokhnaFaty09](https://github.com/SokhnaFaty09) (Data Analyst)

> [Ryan Heuvel](https://github.com/I-love-C) (Data Analyst)
