.PHONY: install run dry-run preview lint clean help

help: ## 显示帮助
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install: ## 安装依赖
	pip3 install -r requirements.txt

run: ## 抓取新闻并发送邮件
	python3 -m src.main

dry-run: ## 仅抓取新闻，不发送邮件 (终端预览)
	python3 -m src.main --dry-run

preview: ## 抓取新闻并保存为 HTML 文件预览
	python3 -m src.main --dry-run -o preview.html
	@echo "HTML 已保存到 preview.html，可用浏览器打开查看"

lint: ## 运行代码检查
	python3 -m py_compile src/config.py
	python3 -m py_compile src/news_fetcher.py
	python3 -m py_compile src/email_builder.py
	python3 -m py_compile src/email_sender.py
	python3 -m py_compile src/main.py
	@echo "All files compile OK"

clean: ## 清理临时文件
	rm -f preview.html
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
