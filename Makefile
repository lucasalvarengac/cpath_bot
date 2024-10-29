.PHONY: init login demo backend deploy codigo-girls push frubana push-zip deploy-zip frubana-dev

VER ?= $(shell git describe --abbrev=0 --tags)
ROLE = "arn:aws:iam::122610507539:role/deploy-role"
REPO = "964959279024.dkr.ecr.sa-east-1.amazonaws.com"
ARCH = $(shell uname -m)
AWS_ARCH = $(ARCH)
ifeq "$(ARCH)" "aarch64"
	AWS_ARCH = "arm64"
endif

%.zip: %/*
	$(eval TMP := $(shell mktemp -d))
	pip install -r $(@:.zip=)/requirements.txt -t $(TMP) --platform="manylinux2014_$(ARCH)" --only-binary=":all:" --upgrade --implementation cp --python-version 3.11
	cp -r $(@:.zip=)/* $(TMP)/
	cd $(TMP) && zip -r $(CURDIR)/$@ .
	rm -rf $(TMP)

push-zip:
	make $(app:-dev=).zip
	aws s3 cp $(app:-dev=).zip s3://lambda-repository-cpath/$(app:-dev=)/$(app:-dev=)-$(VER).zip

deploy-zip: push-zip
	aws lambda update-function-code --function-name $(app) --architectures $(AWS_ARCH) --s3-bucket lambda-repository-cpath --s3-key $(app:-dev=)/$(app:-dev=)-$(VER).zip
	rm $(app:-dev=).zip

push:
	docker push $(REPO)/$(app):$(VER)

deploy: push
	aws lambda update-function-code --function-name $(app) --architectures $(AWS_ARCH) --image-uri $(REPO)/$(app):$(VER)
