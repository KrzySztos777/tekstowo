DROP TABLES tracks,performers,performers_pages;

CREATE TABLE performers (
	id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	tracks_no INT NOT NULL,
	link TEXT NOT NULL
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE tracks (
	id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	performer INT NOT NULL,
	name VARCHAR(255) NOT NULL,
	yt_id_available ENUM('YES','NO') NOT NULL,
	yt_id VARCHAR(255),
	link TEXT NOT NULL,
	page_no INT NOT NULL,
	FOREIGN KEY (performer) REFERENCES performers(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE performers_pages (
	letter VARCHAR(15),
	page INT,
	tracks_no INT
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*
select performers.* from tracks right join performers on performers.id=tracks.performer group by performers.id  having count(tracks.id)<performers.tracks_no;


select count(*),sum(performers_pages.tracks_no) from performers_pages;

select 'udane' as 'x', count(*) as 'pages',sum(performers_pages.tracks_no) as 'performers' from performers_pages where tracks_no>=0 union select 'nieudane',count(*) ,'?' from performers_pages where tracks_no=-1;
*/
