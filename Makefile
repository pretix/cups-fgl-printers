all: ppds

ppds:
	LC_ALL=C ppdc -z drivers/*
