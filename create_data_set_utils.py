import os
import subprocess
import pandas as pd
import tokenize


def unpack_siva_files_and_checkout_git_repos(dir_path):
    dir_list = os.listdir(dir_path)
    for dir_name in dir_list:
        _extract_siva_files_directory(dir_name, dir_path)


def get_python_files_paths(dir_path):
    all_python_files_list = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".py"):
                all_python_files_list.append(os.path.join(root, file))
    return all_python_files_list


def create_python_files_df(all_python_files_list):
    python_files_paths_series = pd.Series(all_python_files_list)
    python_files_base_names_series = python_files_paths_series.apply(os.path.basename)
    python_files_df = pd.DataFrame([python_files_paths_series, python_files_base_names_series]).T
    python_files_df.columns = ['file_path', 'file_base_name']
    python_files_df['file_size'] = python_files_df.file_path.apply(os.path.getsize)
    python_files_df['number_of_lines'] = python_files_df.file_path.apply(_get_file_number_of_lines)
    return python_files_df


def create_tokens_df(python_files_df):
    tokens_df_temp = python_files_df.file_path.apply(_get_tokens_df)
    tokens_df = pd.concat(tokens_df_temp.values)
    tokens_df.file_path = tokens_df.file_path.astype("category")
    tokens_df.type_name = tokens_df.type_name.astype("category")
    return tokens_df


def _get_file_number_of_lines(file_path):
    return len(open(file_path, 'rb').readline())


def _get_tokens_df(file_path):
    tokens_df = \
        pd.DataFrame(
            {},
            columns=['type_name', 'string', 'start', 'end', 'line', 'file_path', 'line_index'])
    try:
        tokens_list = []
        with open(file_path, 'rb') as f:
            for five_tuple in tokenize.tokenize(f.readline):
                token_dict = {
                    'type_name': tokenize.tok_name[five_tuple.type],
                    'string': five_tuple.string,
                    'start': five_tuple.start,
                    'end': five_tuple.end,
                    'line': five_tuple.line,
                    'file_path': file_path,
                    'line_index': five_tuple.start[0]}
                tokens_list.append(token_dict)
        tokens_df = pd.DataFrame(tokens_list)
    except:
        print(file_path)
        pass
    return tokens_df


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
