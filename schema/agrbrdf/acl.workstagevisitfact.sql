--
-- Name: workstagevisitfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE workstagevisitfact FROM PUBLIC;
REVOKE ALL ON TABLE workstagevisitfact FROM agrbrdf;
GRANT ALL ON TABLE workstagevisitfact TO agrbrdf;
GRANT SELECT ON TABLE workstagevisitfact TO gbs;


--
-- PostgreSQL database dump complete
--

