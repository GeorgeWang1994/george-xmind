# -*- coding: utf-8 -*-
import fnmatch
import os
import re
from collections import defaultdict

import xmind
from xmind.core.topic import TopicElement

DEFAULT_DJANGO_PROJECT_PATH = ''
DEFAULT_PROJECT_NAME = ''
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.join(BASE_DIR, 'george-xmind')


class Gxmind(object):
    """
    用来处理节点的操作
    """
    def __init__(self, path):
        self.path = path
        self.wb = xmind.load(self.path)
        self.sheet = self.wb.createSheet()
        self.sheet.setTitle('画布')
        self.wb.addSheet(self.sheet)
        self.root = self.sheet.getRootTopic()
        self.root.setTitle(DEFAULT_PROJECT_NAME)
        self.clear()

    def create_sub(self, title='', content=''):
        """
        创建子节点
        :param title: 标题
        :param content: 备注信息
        :return: 子节点
        """
        sub = TopicElement()
        sub.setTitle(title)
        if content:
            sub.setPlainNotes(content)
        return sub

    def add_sub(self, child, parent=None):
        parent = parent or self.root
        parent.addSubTopic(topic=child)

    def save(self):
        xmind.save(self.wb, self.path)

    def clear(self):
        for sheet in self.wb.getSheets():
            self.wb.removeSheet(sheet)


gxmind = Gxmind(os.path.join(PROJECT_ROOT, DEFAULT_PROJECT_NAME + '.xmind'))


def find_files_recursively(root_path, filename='', prefix='', suffix='.py'):
    """
    递归的查找文件
    :param root_path: 文件路径
    :param filename: 需要搜索的文件名
    :param prefix: 文件名前缀
    :param suffix: 文件名后缀
    :return: 搜索出的文件
    """
    matches = {}
    for root, dir_names, file_names in os.walk(root_path):
        m_module = root.strip().split('/')[-1]
        for name in fnmatch.filter(file_names, prefix + filename + suffix):
            matches[m_module] = os.path.join(root, name)

    return matches


def match_regex(string):
    """
    正则匹配
    :param string:
    :return: 匹配结果
    """
    return re.findall(r"^class (\w+)\((.+)\):", string, flags=re.MULTILINE)


def get_one_file_models(file_path):
    """
    获取一个model文件中的model
    :param file_path:
    :return: model数组
    """
    result = []
    with open(file_path, 'r+') as fp:
        match = match_regex(fp.read())
        for child, parent in match:
            result.append({child: parent})

    return result


def get_models(matches):
    """
    获取所有的model
    :param matches:
    :return: model数组
    """
    all_models = defaultdict(list)

    for m_module, m_path in matches.items():
        if not os.path.exists(m_path):
            continue

        models = get_one_file_models(m_path)
        all_models[m_module].extend(models)

    return all_models


def handle_models(models):
    """
    绘制model的思维导图
    :param models: model数组
    :return:
    """
    model_root = gxmind.create_sub(title='models')
    gxmind.add_sub(child=model_root)

    for m_module, items in models.items():
        parent = gxmind.create_sub(title=m_module)
        gxmind.add_sub(child=parent, parent=model_root)

        if not items:
            continue

        for item in items:
            for key in item.keys():
                child = gxmind.create_sub(title=key)
                gxmind.add_sub(child=child, parent=parent)

    gxmind.save()


def run():
    if not os.path.exists(DEFAULT_DJANGO_PROJECT_PATH):
        print u"请先设置项目路径!"
        return

    if not DEFAULT_PROJECT_NAME:
        print u'请先设置项目名称'
        return

    matches = find_files_recursively(DEFAULT_DJANGO_PROJECT_PATH, filename='models')
    models = get_models(matches)
    handle_models(models)


if __name__ == '__main__':
    run()
