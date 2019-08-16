--
-- Name: databasesearchobservation; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE databasesearchobservation FROM PUBLIC;
REVOKE ALL ON TABLE databasesearchobservation FROM agrbrdf;
GRANT ALL ON TABLE databasesearchobservation TO agrbrdf;
GRANT SELECT ON TABLE databasesearchobservation TO gbs;


