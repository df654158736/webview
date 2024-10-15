import logging


class SeleniumLogger:
    def __init__(self, log_file_path):
        """
        初始化日志记录器类。

        :param log_file_path: 保存日志文件的路径。
        """
        self.logger = logging.getLogger('selenium')
        self.logger.setLevel(logging.INFO)
        self.log_file_path = log_file_path
        self.setup_logger()

    def setup_logger(self):
        """
        设置日志记录器，将日志写入文件，并输出到控制台。
        """
        # 创建一个文件处理器，用于写入日志文件
        file_handler = logging.FileHandler(
            self.log_file_path, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        # 创建一个流处理器，用于将日志输出到控制台
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)

        # 创建一个日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        # 将文件处理器和流处理器添加到日志记录器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

    def log(self, message):
        """
        记录日志信息。

        :param message: 要记录的日志信息。
        """
        self.logger.info(message)


# 使用示例
if __name__ == '__main__':
    log_file_path = 'selenium.log'

    # 创建SeleniumLogger实例
    selenium_logger = SeleniumLogger(log_file_path)

    # 清除日志处理器，防止重复添加
    selenium_logger.logger.handlers.clear()
