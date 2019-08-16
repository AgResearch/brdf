--
-- Name: databasesearchstudy; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE databasesearchstudy FROM PUBLIC;
REVOKE ALL ON TABLE databasesearchstudy FROM agrbrdf;
GRANT ALL ON TABLE databasesearchstudy TO agrbrdf;
GRANT SELECT ON TABLE databasesearchstudy TO gbs;


