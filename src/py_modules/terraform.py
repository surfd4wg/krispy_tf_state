import os
from pathlib import Path
import subprocess
import shutil

class TfCmd:
    def __init__(self, backend_config=None, extra_args=None, force=True, prefix_args=None, module_import=None):
        super().__init__()
        self.backend_config = backend_config
        self.extra_args = extra_args
        self.force = force
        self.module_import = module_import
        self.prefix_args = prefix_args

    
    def invoke_cmd(self):
        process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
        poll = process.poll() is None
        for line in process.stdout:
            print(line)
        return poll

    def tf_apply(self):
        self.cmd = "terraform apply"
        if self.force == True:
            self.cmd = f"{self.cmd} -auto-approve"
        else:
            pass
        if self.extra_args is not None:
            self.cmd = f"{self.cmd} {self.extra_args}"
        else:
            pass
        self.invoke_cmd()

    def tf_destroy(self):
        self.cmd = "terraform destroy"
        if self.force == True:
            self.cmd = f"{self.cmd} -auto-approve"
        else:
            pass
        if self.extra_args is not None:
            self.cmd = f"{self.cmd} {self.extra_args}"
        else:
            pass
        self.invoke_cmd()

    def tf_import(self):
        if self.module_import is None:
            raise SystemExit("terraform module to import is required")
        else:
            self.cmd = f"terraform import {self.module_import}"
        self.invoke_cmd()

    def tf_init(self):
        self.cmd = "terraform init"
        if self.backend_config is not None:
            self.cmd = f"{self.cmd} -backend-config=\"{self.backend_config}\""
        else:
            pass
        if self.prefix_args is not None:
            self.cmd = f"{self.prefix_args} {self.cmd}"
        self.invoke_cmd()
    
    def tf_plan(self):
        self.cmd = "terraform plan"
        self.invoke_cmd()

    def tf_state_pull(self):
        self.cmd = "terraform state pull"
        self.invoke_cmd()

class TfFiles:
    def __init__(self, client=None, bucket_name=None, table_name=None, region=None, file_name=None):
        super().__init__()
        self.client = client
        self.region = region
        self.bucket_name = bucket_name
        self.file_name = file_name
        self.table_name = table_name

    def tf_backend_config(self):
        if self.file_name is None:
            self.file_name = f"s3.{self.region}.tfbackend"
        else:
            pass

        data = f"""
        bucket          = \"{self.bucket_name}\"
        dynamodb_table  = \"{self.table_name}\"
        region          = \"{self.region}\"
        key             = "state/terraform.tfstate"
        encrypt         = \"true\"
        """
        with open(self.file_name, "w") as file:
            file.write(data)

    def tf_vars(self):
        if self.file_name is None:
            self.file_name = "terraform.tfvars"
        else:
            pass
        if self.client is None:
            raise SystemExit("value for client is required")
        else:
            pass
        data = f"""
        client = \"{self.client}\"
        """
        with open(self.file_name, "w") as file:
            file.write(data)

    def remove_tf_directory():
        dir_path = Path(__file__).parent
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
        else:
            pass

    def comment_backend(self):
        if self.file_name is None:
            self.file_name = "terraform.tf"
        else:
            pass
        file = Path(self.file_name)
        text = file.read_text()
        text = text.replace("backend", "#backend")
        file.write_text(text)

    def uncomment_backend(self):
        if self.file_name is None:
            self.file_name = "terraform.tf"
        else:
            pass
        file = Path(self.file_name)
        text = file.read_text()
        text = text.replace("#", "")
        file.write_text(text)
        
        
