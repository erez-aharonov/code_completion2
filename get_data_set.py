import os
import subprocess


def unpack_siva_files_and_checkout_git_repos(dir_path):
    dir_list = os.listdir(dir_path)
    for dir_name in dir_list:
        _extract_siva_files_directory(dir_name, dir_path)


def _extract_siva_files_directory(dir_name, dir_path):
    directory_files_list, full_dir_path = _get_directory_files_list(dir_name, dir_path)
    for file_name in directory_files_list:
        file_full_path = os.path.join(full_dir_path, file_name)
        if _is_siva_file(file_full_path, file_name):
            _extract_single_sive_file(full_dir_path, file_name, file_full_path)


def _is_siva_file(file_full_path, file_name):
    return file_name.endswith(".siva") and os.path.isfile(file_full_path)


def _get_directory_files_list(dir_name, dir_path):
    full_dir_path = os.path.join(dir_path, dir_name)
    directory_files_list = os.listdir(full_dir_path)
    print(full_dir_path, directory_files_list)
    return directory_files_list, full_dir_path


def _extract_single_sive_file(full_dir_path, file_name, file_full_path):
    git_bare_repo_path = _create_bare_git_directory(file_name, full_dir_path)
    git_repo_path = _create_git_directory(full_dir_path, file_name)
    _unpack_siva(file_full_path, git_bare_repo_path)
    _extract_git_repo(git_bare_repo_path, git_repo_path)


def _extract_git_repo(git_bare_repo_path, git_repo_path):
    _clone_git(git_bare_repo_path, git_repo_path)
    os.chdir(git_repo_path)
    output = _branch_git()
    _checkout_git(output)


def _unpack_siva(file_full_path, git_bare_repo_path):
    siva_bash_command = "siva unpack {} {}".format(file_full_path, git_bare_repo_path)
    _run_bash_command(siva_bash_command)


def _create_bare_git_directory(file_name, full_dir_path):
    git_bare_repo_path = os.path.join(full_dir_path, "temp_git_bare_repo_{}").format(file_name)
    os.makedirs(git_bare_repo_path)
    return git_bare_repo_path


def _create_git_directory(full_dir_path, file_name):
    git_repo_path = os.path.join(full_dir_path, "temp_git_repo_{}").format(file_name)
    os.makedirs(git_repo_path) 
    return git_repo_path


def _clone_git(git_bare_repo_path, git_repo_path):
    git_clone_command = "git clone {} {}".format(git_bare_repo_path, git_repo_path)
    _run_bash_command(git_clone_command)


def _branch_git():
    git_branch_command = r"git branch -a"
    output = _run_bash_command(git_branch_command)
    print(output)
    return output


def _checkout_git(output):
    git_checkout_command = "git checkout {}".format(output.split(b"\n")[0].strip().decode("utf-8"))
    _run_bash_command(git_checkout_command)


def _run_bash_command(bash_command):
    print(bash_command)
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return output
