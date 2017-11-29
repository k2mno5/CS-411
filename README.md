# CS-411
[![Build Status](https://semaphoreci.com/api/v1/projects/72100769-7cea-4fdb-be54-dc5f7829c3dc/1600858/badge.svg)](https://semaphoreci.com/stackquora411/cs-411) [![Code Coverage](https://github.com/k2mno5/CS-411/blob/develop/coverage.svg)](https://github.com/k2mno5/CS-411/blob/develop/test_report.txt)

## Please work on your own branch (or forked repo) for local development
* Implementing functionalities and updates on your branch
* Creating Pull Request (PR) for merging changes into develop branch
* Merging PR after passing tests and code review
* Once a milestone is hit, the develop branch will be merged to master branch (release branch)

### Note:
* models.py is preserved for MySQL table for now until we testify that including intermediate classes will not affect database construction in tests.
  * Until then, we should use other files or "model" folder for holding those intermediate classes
* We should implement most of the internal functionalities in controller.py to hide the somewhat complicated logic from API caller. In this case:
  * view.py is only responsible for getting request from API caller, calling corresponding functions in controller.py and return the final results.
  * controller.py is responsible to interacting with database (instances of models.py), updating intermediate information (cashes) and returning corresponding information.
  * models.py (and/or other model files) is the "schema" of the data structure we are dealing with.
  
### How to test your code
* Ideally, you should write the test cases before implementing your functions: what output do I expect to get if specific input is provided and what are the edge cases.
* Write the test cases:
  * Creating mock data
  * Call the function to be tested with the mock data
  * Assert the result to be the same as expected value
* run `python manage.py test`

**Note: testing will be triggerred automatically as long as you have your test cases and code pushed to develop branch**
