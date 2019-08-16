--
-- Name: scratch; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE scratch FROM PUBLIC;
REVOKE ALL ON TABLE scratch FROM agrbrdf;
GRANT ALL ON TABLE scratch TO agrbrdf;
GRANT SELECT ON TABLE scratch TO gbs;


