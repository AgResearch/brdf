--
-- Name: gene2accession; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE gene2accession FROM PUBLIC;
REVOKE ALL ON TABLE gene2accession FROM agrbrdf;
GRANT ALL ON TABLE gene2accession TO agrbrdf;
GRANT SELECT ON TABLE gene2accession TO gbs;


