# MetagenoMongo

MetagenoMongo is an automated data error correction tool. It aims to ensure data accuracy and integrity by automating the detection and correction of common errors found in datasets sourced from multiple origins. Additionally, MetagenoMongo offers functionalities for adding, updating, or deleting data, making it capable of creating and managing datasets. Moreover, the tool includes a template generation function for users who prefer alternative editors like Excel, providing correct column names.


## Configuration

Before using MetagenoMongo, ensure that the [.metagenomongo.csv](https://github.com/DEpt-metagenom/MetagenoMongo/blob/main/.metagenomongo.csv) file is placed within the same directory as the Python script. The [metagenomongo.py](https://github.com/DEpt-metagenom/MetagenoMongo/blob/main/metagenomongo.py) uses PySimpleGUI 4.60.5.

### .metagenomongo.csv

The [.metagenomongo.csv](https://github.com/DEpt-metagenom/MetagenoMongo/blob/main/.metagenomongo.csv) file is a crucial component of the [metagenomongo.py](https://github.com/DEpt-metagenom/MetagenoMongo/blob/main/metagenomongo.py) script. This file enables us to define various input types without the need for code editing. It distinguishes between multiple types of input, including non-writable textbox, writable textbox, non-writable combobox, and writable combobox.

#### Structure

1. Column 1 (Header Name) - The column names.

2. Column 2 (Data Type) - Specifies the type of data contained within the column. **[NOT USED]**

3. Column 3 (Options) - Indicates potential options or values that the column may contain.

4. Column 4 (Type) - Differentiates between fixed and dynamic columns.

#### Adding new items

- Non-writable textbox (e.g. _id) - `_id,string,,fix` - This type of data should not be edited by the user.

- Writable textbox (e.g. projectID) - `projectID,string,,dynamic` -  Users can input data into this type of textbox.

- Non-writable combobox (e.g. source_type) - `source_type,string,"Human,Animal,Food,Environmental,Other,Missing,Not applicable,Not collected,Not provided,",fix` - Users can select from predefined options in this combobox.

- Writable combobox (e.g. platform) - `platform,string,"Nanopore MinION,PacBio HiFi,Illumina MiSeq,Illumina NextSeq500,",dynamic` - Users can both select from predefined options and input their own data into this combobox.


## Usage

1. Import data (.csv or .xlsx) or add/update/delete entries within the app

2. Run correction to correct common errors

3. Correct errors that cannot be corrected automatically

4. Save the dataset (.csv)
