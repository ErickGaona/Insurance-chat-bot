## AWS Credentials Setup Guide for Boto3

This guide will help you configure your AWS credentials on your local machine so that Python tools like boto3 can securely access AWS resources. The recommended method is to use the credentials file.

---

### **Method 1: AWS Credentials File (Recommended)**

This is the safest and most standardized way to manage your credentials, as it stores your keys in a configuration file separate from your code.

#### **Step 1: Locate or Create the `.aws` Directory**

**On Windows:**
- Open File Explorer and go to your user directory (usually `C:\Users\your-username`).
- Create a new folder named `.aws`.

**On macOS / Linux:**
- Open the Terminal and run:
  ```bash
  mkdir ~/.aws
  ```

---

#### **Step 2: Create the `credentials` File**

Inside the `.aws` directory, you need a file named `credentials` (without any extension).

**On Windows:**
- Open Notepad.
- Copy and paste the following content, replacing `[your_access_key_id]` and `[your_secret_access_key]` with your actual credentials.
- Save the file as `C:\Users\your-username\.aws\credentials` (make sure the name is just `credentials`, not `credentials.txt`).

**On macOS / Linux:**
- Open the Terminal and run:
  ```bash
  nano ~/.aws/credentials
  ```
- Copy and paste the following content, replacing the placeholders:

  ```
  [default]
  aws_access_key_id = [your_access_key_id]
  aws_secret_access_key = [your_secret_access_key]
  ```

---

#### **Step 3 (Optional): Set Your Default Region**

You can also create a file named `config` in the same `.aws` directory to specify your default region:

```
[default]
region = us-east-1
```
> **Note:** Replace `us-east-1` with the region appropriate for your resources.

---

### **Method 2: Environment Variables (Quick Alternative)**

This method is useful for quick tests or temporary use, but **is not recommended** for production environments.

**On Windows (Command Prompt):**
```cmd
set AWS_ACCESS_KEY_ID=[your_access_key_id]
set AWS_SECRET_ACCESS_KEY=[your_secret_access_key]
```

**On Windows (PowerShell):**
```powershell
$env:AWS_ACCESS_KEY_ID="[your_access_key_id]"
$env:AWS_SECRET_ACCESS_KEY="[your_secret_access_key]"
```

**On macOS / Linux (Terminal):**
```bash
export AWS_ACCESS_KEY_ID=[your_access_key_id]
export AWS_SECRET_ACCESS_KEY=[your_secret_access_key]
```
> Environment variables only persist for the current terminal session. If you close the window, you will need to set them again.

---

### **Verification**

To check that your credentials are configured correctly, you can use a simple Python script with boto3. If the script runs without authentication errors, you are ready to go!

```
import boto3

sts = boto3.client('sts')
print(sts.get_caller_identity())
```

---

**Done! With these steps, your environment will be ready to access AWS services using boto3.**