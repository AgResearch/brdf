--
-- Name: bioprotocolob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE bioprotocolob FROM PUBLIC;
REVOKE ALL ON TABLE bioprotocolob FROM agrbrdf;
GRANT ALL ON TABLE bioprotocolob TO agrbrdf;
GRANT SELECT ON TABLE bioprotocolob TO gbs;


