class Constants():

    project_status = {
        'Active': 1,
        'Inactive': 2,
        'Archived': 3
        }
    launch_status = {
        'Failed': 1,
        'In Process': 2,
        'Successful': 3
        }
    test_suite_status = {
        'Failed': 1,
        'Successful': 2,
        'Running': 3
        }
    test_run_status = {
        'Failed': 1,
        'Passed': 2,
        'Running': 3
        }
    test_status = {
        'Failed': 1,
        'Passed': 2,
        'Running': 3,
        'Incomplete': 4,
        'Skipped': 5
        }
    test_resolution = {
        'Not set': 1,
        'Working as expected': 2,
        'Test Issue': 3,
        'Environment Issue': 4,
        'Application Issue': 5
        }
