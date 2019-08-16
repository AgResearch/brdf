--
-- Name: uriob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE uriob FROM PUBLIC;
REVOKE ALL ON TABLE uriob FROM agrbrdf;
GRANT ALL ON TABLE uriob TO agrbrdf;
GRANT SELECT ON TABLE uriob TO gbs;


