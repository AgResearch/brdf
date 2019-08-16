--
-- Name: datasourceob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE datasourceob FROM PUBLIC;
REVOKE ALL ON TABLE datasourceob FROM agrbrdf;
GRANT ALL ON TABLE datasourceob TO agrbrdf;
GRANT SELECT ON TABLE datasourceob TO gbs;


