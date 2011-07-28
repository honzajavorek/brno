<?php


/**
 * Model.
 */
class Model extends Nette\Object
{

	/** @var Nette\Database\Connection */
	protected $db;


	static protected $icons = array(
		// sources
		'http://brnonow.com' => 'icon-brnonow.png',
		'http://poznejbrno.cz' => 'icon-poznejbrno.png',
		'http://www.agartha.cz' => 'icon-agartha.png',
		'http://www.kafelanka.cz' => 'icon-kafelanka.png',
		'http://www.podzemi.brno.cz' => 'icon-underground.png',
	);



	public function __construct(Nette\Database\Connection $database)
	{
		$this->db = $database;
	}

	public function getIconsBySources(array $urls)
	{
		$icons = array();
		foreach ($urls as $url) {
			$filename = self::$icons[$url];
			$icons[] = (object)array(
				'id' => Nette\Utils\Strings::webalize($filename),
				'filename' => $filename,
			);
		}
		return $icons;
	}

	public function getBySources(array $urls)
	{
		// get articles
		$sql = '
			SELECT a.*, ia.place_id, p.lat, p.lng, s.url AS source
			FROM article AS a
			JOIN source AS s
			ON a.source_id = s.id
			JOIN is_about AS ia
			ON ia.article_id = a.id
			JOIN place AS p
			ON ia.place_id = p.id
			WHERE s.url IN (?)
		';

		$pm = array();
		$articles = $this->db->query($sql, $urls)->fetchAll();

		// get tags
		$places = array();
		foreach ($articles as $article) {
			$places[] = $article->place_id;
		}

		$sql = '
			SELECT t.*, ht.place_id
			FROM tag AS t
			JOIN has_tag AS ht
			ON ht.tag_id = t.id
			WHERE ht.place_id IN (?)
		';
		$tags = array();
		foreach ($this->db->query($sql, $places) as $tag) {
			if (isset($tags[$tag->place_id])) {
				$tags[$tag->place_id][] = $tag;

			} else {
				$tags[$tag->place_id] = array($tag);
			}
		}

		// prepare placemarks
		foreach ($articles as $article) {
			$pm[] = (object)array(
				'name' => $article->title,
				'url' => $article->url,
				'photo' => $article->photo_url,
				'tags' => (isset($tags[$article->place_id]))? $tags[$article->place_id] : array(),
				'lat' => $article->lat,
				'lng' => $article->lng,
				'icon' => Nette\Utils\Strings::webalize(self::$icons[$article->source]),
				'source' => $article->source,
			);
		}

		return $pm;
	}

}
