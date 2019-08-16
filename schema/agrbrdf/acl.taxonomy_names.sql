--
-- Name: taxonomy_names; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE taxonomy_names FROM PUBLIC;
REVOKE ALL ON TABLE taxonomy_names FROM agrbrdf;
GRANT ALL ON TABLE taxonomy_names TO agrbrdf;
GRANT SELECT ON TABLE taxonomy_names TO gbs;


