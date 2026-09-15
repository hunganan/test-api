*** Settings ***
Library           auto_HeadlessDownload
Library           SeleniumLibrary
Library           Collections
#Library           lib.UsmAPI
#Library           lib/ems_v2/os_and_file.py
#Resource          res/ems_v2/selenium.robot
#Resource          res/ems_v2/common.robot
#Resource          res/ems_v2/usmv2/dialog.robot
#Resource          res/ems_v2/usmv2/main_tab.robot
Variables         gconf.py

*** Variables ***
${USMv2_URL}                     https://${G_vsm_mcm}
${DATA_TEST_ID}                  //*[@data-testid="dialog-provider"]
${PROFILE_BUTTON}                //*[@data-testid="profile-button"]
${SIGN_OUT_BUTTON}               ${PROFILE_BUTTON}//div[.="Sign out"]
${SIGN_IN_BUTTON}                ${DATA_TEST_ID}//button[.="Sign in"]
${INPUT_USER_ID}                 ${DATA_TEST_ID}//input[@placeholder="User ID"]
${INPUT_PASSWORD}                ${DATA_TEST_ID}//input[@placeholder="Password"]
${INPUT_CURRENT_PASSWORD}        //input[@data-testid="change-pass--current"]
${INPUT_NEW_PASSWORD}            //input[@data-testid="change-pass--new"]
${INPUT_CONFIRM_NEW_PASSWORD}    //input[@data-testid="change-pass--confirm"]
${SIGN_IN_INFORMATION}           ${DATA_TEST_ID}//div[.="Last signed in time"]
${TIME_ZONE_DROPDOWN_BUTTON}     //input[@data-testid="timezone-selector-container"]//parent::div//button

*** Keywords ***
Initialize USMv2
    [Arguments]    ${id}=${G_vsm_web_login_id}    ${pw}=${G_vsm_web_login_pw}    ${TIME_ZONE}=UTC    ${USMv2_login_ip}=${USMv2_URL}    ${alias}=usmv2
    [Documentation]    _*Description*__
    ...    - Initialize USMv2
    ...
    ...    _*Arguments*_ : ${id}=${G_vsm_web_login_id}/${pw}=${G_vsm_web_login_pw}
    ...    - ${id}: Id of USMv2 account
    ...    - ${pw}: Password of USMv2 account
    ...
    ...    _*Return Value*_ : None
    ...
    ...    _*Example*_
    ...    - Initialize USMv2
    ...    - Initialize USMv2    abc    1qaz@WSX
    ${open_flag}=    Open USMv2    ${USMv2_login_ip}/login    alias=${alias}
    Login USMv2    ${id}    ${pw}    ${TIME_ZONE}
    RETURN    ${open_flag}

Terminate USMv2
    [Documentation]    _*Documentation*_
    ...    - This keyword Terminate USMv2
    ...
    ...    _*Arguments*_
    ...    - None
    ...
    ...    _*Return Value*_
    ...    - None
    ...
    ...    _*Example*_
    ...    - Terminate USMv2
    ...
    [Timeout]    3 min
    Log    Terminating VSM    console=yes
    Run Keyword And Ignore Error    Logout USMv2
    Run Keyword And Ignore Error    Close all Browsers
    Log    Terminate VSM successful   console=yes

Open Web Url
    [Arguments]    ${url}=${web_url}    ${browser}=chrome    ${alias}=browse1    ${expect_element}=${SIGN_IN_BUTTON}
    [Documentation]    _*Description*_
    ...    - Open Web Url and Maximize window.
    ...    - If "G_lsm_running_location" is jenkins or anything except local, try to open lsm 10 times.
    ...
    ...    _*Arguments*_ : ${url}=${web_url} | ${browser}=chrome | ${alias}=browse1
    ...    - ${url} : VSM URL which is connected
    ...    - ${browser} : [ _lower case browser name_ ] it is support only chrome now..
    ...    - ${alias} : vsm or cms or ...
    ...
    ...    _*Return Value*_ : None
    Log    Open Chrome...Please wait    console=yes
    ${dc}    Evaluate    sys.modules['selenium.webdriver'].DesiredCapabilities.CHROME    sys, selenium.webdriver
    Set To Dictionary    ${dc}    acceptInsecureCerts    ${True}
    ${options}    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver
    Call Method    ${options}    add_argument    disable-popup-blocking
    Call Method    ${options}    add_argument    incognito
    Call Method    ${options}    add_argument    disable-application-cache
    Call Method    ${options}    add_argument    lang\=en-us
    Call Method    ${options}    add_argument    disable-infobars
    Call Method    ${options}    add_argument    start-maximized
    ${list}    Create list    enable-automation
    Call Method    ${options}    add_experimental_option    excludeSwitches    ${list}
    Call Method    ${options}    add_experimental_option    useAutomationExtension    ${FALSE}
    Run Keyword If    '${G_headed_or_headless}'=='headless'    Call Method    ${options}    add_argument    headless
    Run Keyword If    '${G_headed_or_headless}'=='headless'    Call Method    ${options}    add_argument    disable-gpu
    Call Method    ${options}    add_argument    window-size\=${G_window_size}
    ${prefs} =    Create Dictionary    download.default_directory=${OUTPUT DIR}
    Call Method    ${options}    add_experimental_option    prefs    ${prefs}
    FOR    ${key}    ${value}    IN    &{dc}
        Call Method    ${options}    set_capability    ${key}    ${value}
    END
    ${browser_index}=    Create Webdriver    Chrome    options=${options}    alias=${alias}
    Enable Download In Headless Chrome    ${browser_index}    ${OUTPUT DIR}
    FOR    ${i}    IN RANGE    5
        ${browser_index}=    Go To    ${url}
        Set Selenium Timeout    10s
        ${stt}    run keyword and return status    Wait Until Element Is Visible    ${expect_element}    15s
        EXIT FOR LOOP IF    ${stt}
    END
    should be true    ${stt}    Login button didnot appear after timeout
    Log    Open Chrome successful.    console=yes
    RETURN    ${browser_index}

Login USMv2
    [Arguments]    ${id}=${G_vsm_web_login_id}    ${pw}=${G_vsm_web_login_pw}    ${TIME_ZONE}=UTC    ${close_user_id}=${G_vsm_web_login_id}
    [Documentation]    _*Description*__
    ...    - Login USMv2
    ...
    ...    _*Arguments*_ : ${id}=${G_vsm_web_login_id}/${pw}=${G_vsm_web_login_pw}
    ...    - ${id}: Id of USMv2 account
    ...    - ${pw}: Password of USMv2 account
    ...
    ...    _*Return Value*_ : None
    ...
    ...    _*Example*_
    ...    - Login USMv2
    ...    - Login USMv2    abc    1qaz@WSX
    Log    Log-in to USM...     console=yes
    Wait Until Element Is Visible    ${SIGN_IN_BUTTON}
    Input Login Id And Password    ${id}    ${pw}    ${INPUT_USER_ID}    ${INPUT_PASSWORD}
    Select Dropdown    ${TIME_ZONE_DROPDOWN_BUTTON}    ${TIME_ZONE}
    Click Button    ${SIGN_IN_BUTTON}
    Wait Until Progress Widget Disappeared
    ${Sign_in}    Run Keyword And Return Status    Wait until element is visible     ${DIALOG_ACTION_V2}//span    0.1s
    ${dialog_exists}    Run keyword if    '${Sign_in}'=='True'    Get Element Count    ${DIALOG_CONTENT_V2}
    ${dialog_exists}    Set variable if    '${dialog_exists}'=='None'    0    ${dialog_exists}
    ${dialog_message}    Run Keyword If    ${dialog_exists}>0    Get Element Attribute    ${DIALOG_CONTENT_V2}    textContent
    ${is_same_session}    Run Keyword And Return Status    Should Contain    ${dialog_message}    You can't sign in because sessions in this account are all in use.
    Run Keyword If    ${is_same_session}    Click Element Using Javascript    ${DIALOG_TOOLTIP_CONTAINER}//span[.="${close_user_id}"]
    Run Keyword If    ${is_same_session}    Click Element Using Javascript     ${DIALOG_ACTION_V2}//span[.="Close and sign in"]
    ${is_already_used}    Run Keyword And Return Status    Should Contain    ${dialog_message}     The user ID is already being used.
    Run Keyword If    ${is_already_used}    Click Element Using Javascript     ${DIALOG_ACTION_V2}//span[.="Close and sign in"]
    Wait until keyword succeeds    2x    10s    Wait until element is visible    ${PROFILE_BUTTON}
    Log    Log-in USM successful    console=yes
    RETURN    ${dialog_message}

Logout USMv2
    [Arguments]    ${alias}=usmv2
    [Documentation]    _*Description*_
    ...    - Logout USMv2
    ...
    ...    _*Arguments*_ : ${alias}=usmv2
    ...
    ...    _*Return Value*_ : None
    ...
    ...    _*Example*_
    ...    - Terminate USMv2
    ...
    Switch Browser    ${alias}
    Back To Main Menu
    Close All Dialog USMv2
    Wait Until Element Is Visible And Click Element    ${PROFILE_BUTTON}
    Wait Until Element Is Visible And Click Element    ${SIGN_OUT_BUTTON}
    Wait Until Element Is Visible    ${DIALOG_CONTAINER}
    ${stt}    Confirm Dialog And Click Button    Sign out    The portal will be closed. Are you sure you want to sign out anyway?    Sign out anyway
    Run keyword if    '${stt}'=='False'    Confirm Dialog And Click Button    Sign out    The apps listed below will be closed. Are you sure you want to sign out anyway?    Sign out anyway
    Wait Until Progress Widget Disappeared
    Wait Until Element Is Visible    ${SIGN_IN_BUTTON}

Input Login Id And Password
    [Arguments]    ${id}    ${password}    ${element_ID}    ${element_PW}
    [Documentation]    Input user and password to login. Retry if fail.
    FOR    ${retry}    IN RANGE    0    5
        Set Focus To Element    ${element_ID}
        Input Text    ${element_ID}    ${id}
        ${entered_id} =    Get Element Attribute    ${element_ID}    value
        Input Text     ${element_PW}    ${password}
        Comment    Wait Until Element Is Not Visible    //label[.="Please enter a value between 8 and 15 characters long"]    5s
        ${entered_pw} =    Get Element Attribute     ${element_PW}    value
        ${user_check}    Run Keyword And Return Status    Should Be Equal As Strings    ${id}    ${entered_id}
        ${pass_check}    Run Keyword And Return Status    Should Be Equal As Strings    ${password}    ${entered_pw}
        Exit For Loop If    ${user_check} and ${pass_check}
    END
    Should Be True    ${user_check} and ${pass_check}

Initialize API Session
    [Arguments]    ${url}=${USMv2_URL}
    [Documentation]    *PIC: hoa.duc*
    ...    1. Purpose:
    ...        This keyword used to initialize API session before use API functions
	...        Condition:
    ...        - Need to install UsmAPI before using this keyword. Run bat file:
    ...            //TEAM/ACCESS_TEST_TOOL/Autobot_5G/trunk/nr_main/lib/UsmAPI/dist/install.bat
    ...        - Created an account with username = 'usmapi', password = 'S@msung1te', session count = '200'
    ...    2. Arguments:
    ...        - ${url}: EMS address. Ex: https://128.70.6.84
    ...    3. Return value: none
    ...    4. Example:
    ...        Initialize API Session
    ...
    usm api set hostname    ${USMv2_URL}

Login USMv2 In Case Password Initialized
    [Arguments]    ${id}=${G_vsm_web_login_id}    ${current_pw}=${G_vsm_web_login_pw}    ${new_pw}=S@msung1te    ${TIME_ZONE}=UTC    ${close_user_id}=${G_vsm_web_login_id}    ${expect_message}=Pass
    [Documentation]    _*Description*__
    ...    - Login USMv2 In Case Password Initialized
    ...
    ...    _*Arguments*_ : ${id}=${G_vsm_web_login_id}/${pw}=${G_vsm_web_login_pw}
    ...    - ${id}: Id of USMv2 account
    ...    - ${pw}: Password of USMv2 account
    ...
    ...    _*expect_message*_ : Fail => input popup status
    ...    _*expect_message*_ : Pass => input Pass
    ...
    ...    _*Example*_
    ...    - Login USMv2 In Case Password Initialized
    ...    - Login USMv2 In Case Password Initialized    abc    1qaz@WSX
    Log    Log-in to USM...     console=yes
    Wait Until Keyword Succeeds    10x    0.5s    Wait Until Element Is Visible    ${SIGN_IN_BUTTON}
    Input Login Id And Password    ${id}    ${current_pw}    ${INPUT_USER_ID}    ${INPUT_PASSWORD}
    Select Dropdown    ${TIME_ZONE_DROPDOWN_BUTTON}    ${TIME_ZONE}
    Click Button    ${SIGN_IN_BUTTON}
    Wait Until Progress Widget Disappeared
    Wait Until Element Is Visible    //*[@data-testid="dialog-title"]//*[text()="Password initialized"]
    Input Text     ${INPUT_CURRENT_PASSWORD}    ${current_pw}
    Input Text     ${INPUT_NEW_PASSWORD}    ${new_pw}
    Input Text     ${INPUT_CONFIRM_NEW_PASSWORD}    ${new_pw}
    Click Element    ${DIALOG_ACTION_V2}//*[text()="Change"]
    run keyword if    "${expect_message}"=="Pass"    Wait until keyword succeeds    2x    10s    Wait until element is visible    ${PROFILE_BUTTON}
    return from keyword if    "${expect_message}"=="Pass"    PASS
    ${Sign_in}    Wait until keyword succeeds    2x    2s    Wait until element is visible     //*[text()="${expect_message}"]    0.1s
    Click Element    ${DIALOG_ACTION_V2}//button[@label="OK"]

Login Fail USMv2
    [Arguments]    ${id}=${G_vsm_web_login_id}    ${pw}=${G_vsm_web_login_pw}    ${TIME_ZONE}=UTC    ${close_user_id}=${G_vsm_web_login_id}
    [Documentation]    _*Description*__
    ...    - Login Fail USMv2
    ...
    ...    _*Arguments*_ : ${id}=${G_vsm_web_login_id}/${pw}=${G_vsm_web_login_pw}
    ...    - ${id}: Id of USMv2 account
    ...    - ${pw}: Password of USMv2 account
    ...
    ...    _*Return Value*_ : dialog message when login fail
    ...
    ...    _*Example*_
    ...    - Login Fail USMv2
    ...    - Login Fail USMv2    abc    1qaz@WSX
    Log    Log-in to USM...     console=yes
    Wait Until Element Is Visible    ${SIGN_IN_BUTTON}
    Input Login Id And Password    ${id}    ${pw}    ${INPUT_USER_ID}    ${INPUT_PASSWORD}
    Select Dropdown    ${TIME_ZONE_DROPDOWN_BUTTON}    ${TIME_ZONE}
    Click Button    ${SIGN_IN_BUTTON}
    Wait Until Progress Widget Disappeared
    ${Sign_in}    Run Keyword And Return Status    Wait until element is visible     ${DIALOG_ACTION_V2}//span    0.1s
    ${dialog_exists}    Run keyword if    '${Sign_in}'=='True'    Get Element Count    ${DIALOG_CONTENT_V2}
    ${dialog_exists}    Set variable if    '${dialog_exists}'=='None'    0    ${dialog_exists}
    ${dialog_message}    Run Keyword If    ${dialog_exists}>0    Get Element Attribute    ${DIALOG_CONTENT_V2}    textContent
    click element    ${DIALOG_ACTION_V2}//span[text()="OK"]
    RETURN    ${dialog_message}
*** Test Cases ***
aaaaaaa
    Open Web Url    https://shopee.vn/    expect_element=//*[@class="cart-drawer-container"]
    Click Element    //*[@class="cart-drawer-container"]
    Wait Until Element Is Visible And Click Element    //*[contains(@title,'Chuột không dây')]/parent::*/parent::*/preceding-sibling::*/label
    Capture Page ScreenShot