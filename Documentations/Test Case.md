## ✅ 1. Login Module:
| TC ID | Test Case Description             | Input                                                                      | Expected Output                          | Status (P/F) | Remarks |
| ----- | --------------------------------- | -------------------------------------------------------------------------- | ---------------------------------------- | ------------ | ------- |
| TC01  | Login with valid email & password | Email: [valid@example.com](mailto:valid@example.com)<br>Password: Valid123 | Redirect to user dashboard               |              |         |
| TC02  | Login with invalid credentials    | Email: [fake@example.com](mailto:fake@example.com)<br>Password: WrongPass  | Show error message "Invalid credentials" |              |         |
| TC03  | Leave fields empty                | Email: *blank*<br>Password: *blank*                                        | Show error "Fields cannot be empty"      |              |         |
| TC04  | Role-based redirection            | Login as doctor                                                            | Redirect to Doctor Panel                 |              |         |

## 🛎 2. Admin Panel – Receptionist:
| TC ID | Test Case Description | Input                                     | Expected Output                     | Status (P/F) | Remarks |
| ----- | --------------------- | ----------------------------------------- | ----------------------------------- | ------------ | ------- |
| TC05  | Add new in-patient    | Patient details + doctor + room           | In-patient added, room assigned     |              |         |
| TC06  | Add new out-patient   | Patient details + doctor                  | Out-patient added for appointment   |              |         |
| TC07  | Assign wrong doctor   | Invalid specialty selected                | Show warning "Doctor not available" |              |         |
| TC08  | Add new doctor        | Doctor name, specialization, availability | Doctor added successfully           |              |         |

## 🩺 3. Doctor Panel:
| TC ID | Test Case Description  | Input                            | Expected Output                        | Status (P/F) | Remarks |
| ----- | ---------------------- | -------------------------------- | -------------------------------------- | ------------ | ------- |
| TC09  | View assigned patients | Doctor logs in                   | List of assigned patients is displayed |              |         |
| TC10  | Accept appointment     | Click accept on assigned patient | Status changes to "Accepted"           |              |         |
| TC11  | Reject appointment     | Click reject                     | Status changes to "Rejected"           |              |         |
| TC12  | Prescribe medicine     | Input: medicine name, dosage     | Medicine added to prescription list    |              |         |

## 💊 4. Store Manager Panel:
| TC ID | Test Case Description | Input                          | Expected Output                          | Status (P/F) | Remarks |
| ----- | --------------------- | ------------------------------ | ---------------------------------------- | ------------ | ------- |
| TC13  | View prescriptions    | Store manager logs in          | List of prescribed medicines displayed   |              |         |
| TC14  | Medicine stock update | Medicine prescribed to patient | Stock count decreases automatically      |              |         |
| TC15  | Stock below threshold | Stock < 1                      | Alert "Order more medicine" is displayed |              |         |

## 🔒 5. Logout & Session:
| TC ID | Test Case Description            | Input               | Expected Output                             | Status (P/F) | Remarks |
| ----- | -------------------------------- | ------------------- | ------------------------------------------- | ------------ | ------- |
| TC16  | Logout from any role             | Click Logout        | Redirect to login page, session ended       |              |         |
| TC17  | Session timeout after inactivity | Idle for 10 minutes | Auto-logout user and redirect to login page |              |         |
