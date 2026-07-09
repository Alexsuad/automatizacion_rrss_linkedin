from linkedin_content_system.publishers import (
    ExternalDryRunPublisher,
    LocalDraftPublisher,
    PublicationPublisherPort,
)


def test_localdraftpublisher_cumple_puerto_publicacion(tmp_path):
    publisher = LocalDraftPublisher(base_dir=str(tmp_path))

    assert isinstance(publisher, PublicationPublisherPort)
    assert hasattr(publisher, "guardar")


def test_externaldryrunpublisher_cumple_puerto_publicacion(tmp_path):
    publisher = ExternalDryRunPublisher(base_dir=str(tmp_path))

    assert isinstance(publisher, PublicationPublisherPort)
    assert hasattr(publisher, "guardar")
