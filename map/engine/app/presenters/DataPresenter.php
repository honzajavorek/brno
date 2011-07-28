<?php

/**
 * Data in KML.
 */
class DataPresenter extends BasePresenter
{

	protected function beforeRender()
	{
		$this->setLayout(FALSE);
		$this->context->httpResponse->setContentType($this->context->params['data']['contentType']);

		$url = $this->context->httpRequest->url;
		$this->template->iconPath = 'http://' . $url->authority . $url->basePath . 'images';
	}

	public function renderGrunge()
	{
		$this->template->title = 'Podzemní a tajuplná místa v Brně';

		$sources = array(
			'http://www.agartha.cz',
			'http://www.kafelanka.cz',
			'http://www.podzemi.brno.cz',
		);

		$this->template->placemarks = $this->context->model->getBySources($sources);
		$this->template->icons = $this->context->model->getIconsBySources($sources);
	}

	public function renderInfo()
	{
		$this->template->title = 'Články a tipy o místech v Brně';

		$sources = array(
			'http://brnonow.com',
			'http://poznejbrno.cz',
		);

		$this->template->placemarks = $this->context->model->getBySources($sources);
		$this->template->icons = $this->context->model->getIconsBySources($sources);
	}

	protected function afterRender()
	{
		$this->setView('kml');
	}

}
