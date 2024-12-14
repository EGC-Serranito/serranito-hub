## 📋 PR Title

`<ship|show|ask>-WI <work_item_name>-feature <functionality>`

**PR Type:**  


    - ship: It is used for routine changes in development branches. In these cases, it is not necessary to create a pull request, since the changes are applied directly to the integration branch. Minimal automatic CI validations can be configured to verify basic changes.
    - show: It is used to merge development branches with the continuous integration branch develop in easy or intermediate level tasks. Here a pull request is required with more stringent automatic CI validations, ensuring that the implementation is consistent and correct before integration.
    - ask: It is used in merging development branches with the continuous integration branch for tasks of high or intermediate complexity, as well as in any merge of develop with the main production branch. In these cases, CI validations must be completed successfully and a review by the work team is necessary, with a minimum of one review recommended and even two to ensure the quality of the code before final integration.



---

## 📝 Description  

Explain your implemented changes briefly or detailed (OPTIONAL) AND WAIT FOR WORKFLOWS TO EXECUTE AND PASS 
(IT IS A MUST, NOT A RECOMMENDATION)
