--
-- Name: ontologyob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE ontologyob FROM PUBLIC;
REVOKE ALL ON TABLE ontologyob FROM agrbrdf;
GRANT ALL ON TABLE ontologyob TO agrbrdf;
GRANT SELECT ON TABLE ontologyob TO gbs;


