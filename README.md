
<div style="text-align: center;">
  <img src="app/static/img/logos/logo-dark.svg" alt="Logo">
</div>

# Serranito-hub

Repository of feature models in UVL format integrated with Zenodo and flamapy following Open Science principles - Developed by DiversoLab.

### New Implementation

We are excited to announce several new features that we have integrated into the project to enhance its functionality and user experience. Our team has worked diligently to bring you the following improvements:
- A comprehensive UVL editor for seamless model creation and editing.
- Bot integration to automate routine tasks and improve efficiency.
- A user-friendly dashboard that provides an overview of key metrics and activities.
- A suite of new test cases to ensure robustness and reliability.
- A tag cloud feature for better organization and navigation.
- The ability to view user profiles, enhancing community interaction.
- Fakenodo, a tool for simulating node behaviors.
- Functionality to upload, analyze, and repair UVL files.
- An improved user interface for a more intuitive experience.
- The option to download all datasets in one go.
- Enhanced sign-up validation to ensure secure access.

## Members

This team has been colaboration into 2 teams, serranito-hub1 and serranito-hub2.

| Members Serranito-hub-1 | Work Item |  
|------|-------------------|
| [Calero López, Marina](https://github.com/marcallop7) | View User Profile (Low) |
| [De los Santos Barrera, Elena](https://github.com/eledebar) | Tag Cloud (Low) |
| [Galván Cancio, Daniel](https://github.com/Dangalcan) (coordinator)| New testcases (Medium) |
| [Herencia Solís, Lucas Manuel](https://github.com/luchersol) | UVL editor (Hard) |
| [Robles Russo, Eduardo](https://github.com/edurobrus) | Bot integration (Hard) |
| [Solís Padilla, Isaac](https://github.com/IsaacSolisPadilla) | Dashboard (Medium) |

|Members Serranito-hub-2| Work Item |  
|------|-------------------|
| [García Carballo, Juan](https://github.com/JuaniniGC)  | Rate Datasets (Medium) |
  | [García Escudero, Ángel](https://github.com/Angelgares)  (coordinator)    | Upload, analyse and repair UVL (Hard) |
  | [García Rivero, Andrés Francisco](https://github.com/andgarriv) | Improve UI (Medium) |
  | [Muñoz Rodríguez, Jorge](https://github.com/jormunrod)   | Download all dataset (Hard) and Fakenodo (Hard) |
  | [Pérez Santiago, Alejandro](https://github.com/alepez12)   | Sign up validation (Low) | 



  ## Ubuntu Partition Manual
  
This tutorial will guide you step by step to create a partition on your laptop and install Ubuntu 22.04 while keeping your primary operating system if desired.

----------

## **1. Preliminary Preparations**

Before starting, make sure of the following:

1.  **Backup your data:** Make a backup of your important files in case something goes wrong.
    
2.  **Download Ubuntu 22.04:** Go to the [official Ubuntu site](https://ubuntu.com/download/desktop) and download the Ubuntu 22.04 ISO image.
    
3.  **Create a bootable USB:** Use a tool like [Rufus](https://rufus.ie/) (Windows)  to burn the ISO image to a USB drive (at least 8 GB).
    

----------

## **2. Partition Setup**

### **2.1. Access Disk Management**

1.  On Windows, press `Windows + S` and type **"Disk Management"**.
    
2.  Select **"Create and format hard disk partitions"**.
    

### **2.2. Shrink the Current Partition**

1.  Locate the main partition (usually `C:`).
    
2.  Right-click on it and select **"Shrink Volume"**.
    
3.  Enter the size you want to allocate for Ubuntu (recommended: at least 50 GB).
    
4.  Apply the changes. This will leave unallocated space on your disk.
    

----------

## **3. BIOS/UEFI Setup**

1.  Restart your laptop and access the BIOS/UEFI by pressing the appropriate key (usually `F2`, `F12`, `Delete`, or `Esc` depending on the manufacturer).
    
2.  Ensure **Secure Boot** is disabled.
    
3.  Change the boot order so that the USB drive is the first option.
    

Save the changes and restart with the USB drive connected.

----------

## **4. Installing Ubuntu 22.04**

### **4.1. Boot from USB**

1.  Upon restart, you should see the Ubuntu boot menu.
    
2.  Select **"Try Ubuntu without installing"** to test Ubuntu before installing it.
    

### **4.2. Start the Installer**

1.  Double-click on the **"Install Ubuntu"** icon on the desktop.
    
2.  Select your language and follow the prompts.
    

### **4.3. Installation Options**

1.  When asked for the "Installation type," choose **"Install Ubuntu alongside Windows"**.
    
2.  Select the previously unallocated space.
    
3.  Ubuntu will automatically adjust the necessary partitions (swap, ext4, etc.).
    

### **4.4. Final Configuration**

1.  Follow the instructions to set up your time zone, keyboard, and user account.
    
2.  Wait for the installation to complete. Once done, restart the system.
    

----------

## **5. Verify Dual Boot**

1.  On restart, you should see the GRUB menu where you can select between Ubuntu and Windows.
    
2.  If it does not appear, access the BIOS/UEFI and ensure the primary boot option is Ubuntu.
    

----------

## **6. Post-Installation**

1.  **Update Ubuntu:** Open a terminal (`Ctrl + Alt + T`) and run:
    
    ```
    sudo apt update && sudo apt upgrade
    ```
    
2.  **Install additional software:** Use `sudo apt install` to install necessary tools.
    

----------

  ## Project Objectives

  Let's thoroughly develop each Work Item of the project.

  ### WI View User Profile

  - This feature allows users to view their profile, which includes essential information such as their name, surname, affiliation, Orcid, email, and the number of datasets they have uploaded. Below the profile information, users can see a list of the datasets they have uploaded, with the title and publication type of each one. 
  Additionally, pagination is available to easily navigate through the datasets, making it easier to explore all the datasets the user has contributed. When exploring the datasets, the name of the user who uploaded them is displayed. Users can click on the name to view the profile of the uploader, including the datasets they have uploaded. On the sidebar, there is a tag cloud associated with the tags of each dataset. By clicking on a tag, users can filter datasets by that specific tag.
  
  <div align=center>
    <img src="app/static/img/readme/View User Profile.png" alt="image" width="600"/>
  </div>

### WI Tag Cloud

  -  This feature allows users to explore UVL models through a tag cloud, where the tags represent labels associated with datasets. In a tag cloud, the most frequently used tags appear larger, making it easier to identify the most relevant labels. Users can filter and search in real-time, view descriptions of the feature models associated with each dataset, and download them in various formats such as UVL, Glencoe, Slot, and Dimacs. This provides an interactive way to explore and analyze the feature models linked to different datasets.

   <div align=center>
    <img src="app/static/img/readme/tag2.png" alt="image" width="600"/>
  </div>

  <div align=center>
    <img src="app/static/img/readme/tag.png" alt="image" width="600"/>
  </div>



### WI Rate Datasets

  - This feature allows users to rate each dataset with a score from 0 to 5 stars. When exploring datasets, visual star indicators are displayed, with the number of filled stars corresponding to the dataset’s rating. This provides users with a quick and intuitive way to assess the quality or relevance of datasets based on the community’s ratings.

  <div align=center>
    <img src="app/static/img/readme/Rate.png" alt="image" width="600"/>
  </div>

  <div align=center>
    <img src="app/static/img/readme/Rate2.png" alt="image" width="600"/>
  </div>


### Upload, analyse and repair UVL

  - This feature allows users to upload datasets, validate the syntax of UVL files, and repair any identified issues. It focuses on ensuring the integrity and quality of UVL models through the following capabilities:

-   **Uploading datasets**: Users can upload datasets by providing basic information, including:
    
    -   **Title**  (required).
    -   **Description**.
    -   **Publication type**.
    -   **Publication DOI**.
    -   **Tags**  (separated by commas).
    -   **Authors' details**  (name, affiliation, ORCID).
    -   **UVL models**, which can be uploaded by dragging and dropping files into the interface.
    -   **Syntactic validation**: Once a dataset is uploaded, users can validate the UVL file syntax by clicking the "Check" button. This process involves:
    
      -   Defining the UVL grammar and generating a parser (using **ANTLR**).
      -   Analysing the file to identify and display syntax errors.
      -   Providing tools for error correction and revalidation (using  **Flamapy**).

This comprehensive approach ensures that datasets are properly validated and that any issues are efficiently identified and resolved, improving the overall reliability of UVL models.

  <div align=center>
    <img src="app/static/img/readme/Upload, analyse and repair UVL.png" alt="image" width="600"/>
  </div>

  <div align=center>
    <img src="app/static/img/readme/Upload, analyse and repair UVL2.png" alt="image" width="600"/>
  </div>

### Improve UI
  
  - This feature aims to optimize the user experience when interacting with the platform, focusing on the design and usability of the dataset listing. The implemented improvements include:

-   **Dataset sorting**: Users can now sort the contents based on the following criteria:
    
    -   Newest first.
    -   Oldest first.
    -   Alphabetical order (A-Z or Z-A).
    -   Fewest feature models first.
    -   Most feature models first.
-   **Visual redesign**: The top bar, toolbar, and dataset listing have been redesigned to resemble GitHub's style, offering a more modern and familiar user experience.
    
-   **Dark mode**: A dark mode has been added, providing an alternative visualization that enhances accessibility and reduces eye strain, especially in low-light environments.
    

These improvements ensure more intuitive and efficient navigation, along with a more attractive and user-focused design.

  <div align=center>
    <img src="app/static/img/readme/ImproveUI-1.png" alt="image" width="600"/>
  </div>

   <div align=center>
    <img src="app/static/img/readme/ImproveUI-2.png" alt="image" width="600"/>
  </div>

  ### New testcase
  
  - New test cases have been added to the project with the aim of increasing test coverage by improving Rosemary's testing scripts. This includes the creation of a script to insert data into an external database, another to run the application, and a third for the coverage report, which runs all the tests and displays and updates the coverage report. In addition, unit and integration tests have been performed, especially on the dataset, webhook, and Zenodo modules, and a bug has been fixed in the authentication (auth) module. Locust tests have also been added to the user profile (profile), along with Selenium tests to ensure the proper functioning of features in a controlled environment.

 ### UVL editor
  
  -    This feature provides a graphical and interactive way to edit UVL models. By clicking the "Edit" button, users can modify the content of UVL models directly through a visual interface. Once the edits are complete, users can choose to download the updated file or, if they wish to maintain a version history, they can click the "Save" button to create a new version of the file. This action generates a new dataset, and the user will be redirected to a graphical interface specifically designed to facilitate the creation and editing of UVL models. This tool not only enhances the editing experience but also ensures efficient version control of the models.

  <div align=center>
    <img src="app/static/img/readme/UVL-Editor1.png" alt="image" width="600"/>
  </div>

 <div align=center>
    <img src="app/static/img/readme/UVL-Editor 2.png" alt="image" width="600"/>
  </div>

  
 ### Download all dataset
  
  - This feature allows users to download all the datasets stored in UVLHub in a compressed zip file. To do so, users can click the button provided to download the datasets in one go. Additionally, there are options to download datasets based on specific criteria. Users can filter datasets by a date range by selecting a start and end date, allowing them to download datasets created within that time period. Alternatively, users can download datasets created by a specific user by entering the user's email address. This functionality makes it easy for users to download datasets according to their needs.

  <div align=center>
    <img src="app/static/img/readme/Download all dataset.png" alt="image" width="600"/>
  </div>

### Fakenodo

  -  It is an API integration that enables quick searches in simulated databases. This functionality is useful for both testing and demonstration purposes, providing a secure environment for experimentation without compromising real data. By integrating with the Fakenodo API, it ensures consistent and representative search results, allowing for testing with data volumes that mimic real-world scenarios.

### Sign up validation

  - This feature allows users to register securely by verifying their identity through email validation. The registration interface includes required fields for entering the name, surname, email, and password. The system validates the provided email address to ensure it is valid and correctly associated with the user. Once the registration is complete, a verification email will be sent to the user to confirm their identity before they can fully access the platform. This ensures that the registration process is secure and only verified users can access the application.

  <div align=center>
    <img src="app/static/img/readme/Sign-up-1.png" alt="image" width="600"/>
  </div>

   <div align=center>
    <img src="app/static/img/readme/Sign-up-2.png" alt="image" width="600"/>
  </div>

### Bot integration

  - This feature allows users to integrate their bot with different platforms like Discord and Telegram for notifications and updates based on selected frequencies. Users can choose to receive notifications either in real-time or on a daily basis at 9 AM. In Discord, the bot requires the channel ID, while in Telegram, the bot needs the chat ID, which can be obtained using a bot that provides this information. Users can configure up to 5 different bots with distinct settings, with a limit of 3 features per bot and a maximum of 3 chat channels per bot.

The bot can interact with several features:

-   **Flamapy**: The bot analyzes the latest messages and responds by checking if the model is correctly implemented. Specifically, if you send the bot a message containing the contents of a .uvl file, it can use Flamapy to validate whether the model is correct or not.
-   **Hub Stats**: Users can access statistics related to UVLHub.
-   **Fakenodo**: The bot checks if the connection to Fakenodo is active or not.
-   **Dataset**: The bot fetches and provides detailed information about the user's datasets. The message includes dataset titles, descriptions, publication types, DOIs, and downloadable files in UVL format. Each dataset will be accompanied by a detailed list of features and constraints, with download links for each file. Additionally, the bot allows users to view the content of the .uvl files associated with their datasets.
-   **Auth**: The bot retrieves information about the person who has configured it, ensuring clarity on which user is managing and interacting with the bot.

  <div align=center>
    <img src="app/static/img/readme/Bot integration.png" alt="image" width="600"/>
  </div>


### Dashboard

  - This feature allows users to explore various dashboards in UVLHub by selecting different options. Users can view graphs by author, which includes analyzing datasets and visualizations by author. Additionally, they can explore file size distribution by dataset and track the evolution of visualizations, with the option to filter the data by day, month, or year. The dashboard also provides graphs showing the distribution of datasets based on their publication type and insights into the number of downloads for each dataset. These features offer an interactive and comprehensive way to analyze the data and understand the usage patterns within UVLHub.
  <div align=center>
    <img src="app/static/img/readme/dashboard.png" alt="image" width="600"/>
  </div>

  <div align=center>
    <img src="app/static/img/readme/Dashboard2.png" alt="image" width="600"/>
  </div>

  <div align=center>
    <img src="app/static/img/readme/Dashboard3.png" alt="image" width="600"/>
  </div>

  <div align=center>
    <img src="app/static/img/readme/Dashboard4.png" alt="image" width="600"/>
  </div>
 <div align=center>
    <img src="app/static/img/readme/Dashboard5.png" alt="image" width="600"/>
  </div>


---

You can consult the official documentation of the project at [docs.uvlhub.io](https://docs.uvlhub.io/)
